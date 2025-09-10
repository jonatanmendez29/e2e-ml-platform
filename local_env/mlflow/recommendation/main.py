import pandas as pd
import numpy as np
import mlflow
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate
import logging
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationSystem:
    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.ratings_matrix = None
        self.item_similarity_matrix = None
        self.product_features = None

    def load_data(self):
        """Load user-item interaction data and product features"""
        logger.info("Loading interaction data...")

        # Load interaction data
        interaction_query = """
        SELECT 
            user_id,
            product_id,
            COUNT(*) AS interaction_count,
            SUM(quantity) AS total_quantity,
            SUM(sale_amount) AS total_spent
        FROM sales
        GROUP BY user_id, product_id
        """

        interactions = pd.read_sql_query(interaction_query, self.db_conn)

        # Load product features for content-based filtering
        product_query = """
        SELECT 
            product_id,
            name,
            category,
            price
        FROM products
        """

        products = pd.read_sql_query(product_query, self.db_conn)

        return interactions, products

    def create_utility_matrix(self, interactions):
        """Create user-item utility matrix for collaborative filtering"""
        logger.info("Creating utility matrix...")

        # Create a pivot table of user-item interactions
        utility_matrix = interactions.pivot_table(
            index='user_id',
            columns='product_id',
            values='interaction_count',
            fill_value=0
        )

        return utility_matrix

    def prepare_content_based_features(self, products):
        """Prepare product features for content-based filtering"""
        logger.info("Preparing content-based features...")

        # One-hot encode categorical features
        category_encoded = pd.get_dummies(products['category'], prefix='category')

        # Scale numerical features
        scaler = StandardScaler()
        price_scaled = scaler.fit_transform(products[['price']])

        # Combine features
        product_features = pd.DataFrame(
            price_scaled,
            columns=['price_scaled'],
            index=products['product_id']
        )
        product_features = product_features.join(category_encoded.set_index(products['product_id']))

        # Fill NaN values
        product_features = product_features.fillna(0)

        return product_features

    def generate_content_based_recommendations(self, user_id, n_recommendations=5):
        """Generate content-based recommendations for a user"""
        logger.info(f"Generating content-based recommendations for user {user_id}...")

        # Get products the user has interacted with
        user_interactions = self.ratings_matrix.loc[user_id]
        interacted_products = user_interactions[user_interactions > 0].index.tolist()

        if not interacted_products:
            return []  # No interactions, can't make content-based recommendations

        # Calculate weighted average of item similarities
        user_profile = np.zeros(len(self.product_features.columns))

        for product_id in interacted_products:
            if product_id in self.product_features.index:
                user_profile += self.ratings_matrix.loc[user_id, product_id] * self.product_features.loc[
                    product_id].values

        # Normalize the user profile
        if len(interacted_products) > 0:
            user_profile /= len(interacted_products)

        # Calculate similarity between user profile and all items
        item_scores = cosine_similarity([user_profile], self.product_features.values)[0]

        # Create a DataFrame of item scores
        item_scores_df = pd.DataFrame({
            'product_id': self.product_features.index,
            'score': item_scores
        })

        # Filter out items the user has already interacted with
        item_scores_df = item_scores_df[~item_scores_df['product_id'].isin(interacted_products)]

        # Get top N recommendations
        top_recommendations = item_scores_df.nlargest(n_recommendations, 'score')

        return list(zip(top_recommendations['product_id'], top_recommendations['score']))

    def collaborative_filtering(self, interactions):
        """Collaborative filtering using matrix factorization"""
        logger.info("Running collaborative filtering...")

        # Prepare data for Surprise library
        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(
            interactions[['user_id', 'product_id', 'interaction_count']],
            reader
        )

        # Use SVD algorithm
        algo = SVD()

        # Run cross-validation
        cv_results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=3, verbose=True)

        # Train on full dataset
        trainset = data.build_full_trainset()
        algo.fit(trainset)

        return algo, cv_results

    def generate_collaborative_recommendations(self, algo, user_id, n_recommendations=5):
        """Generate collaborative filtering recommendations for a user"""
        logger.info(f"Generating collaborative recommendations for user {user_id}...")

        # Get all product IDs
        product_ids = self.ratings_matrix.columns.tolist()

        # Get products the user has already interacted with
        user_interactions = self.ratings_matrix.loc[user_id]
        interacted_products = user_interactions[user_interactions > 0].index.tolist()

        # Predict ratings for all products
        predictions = []
        for product_id in product_ids:
            if product_id not in interacted_products:
                pred = algo.predict(user_id, product_id)
                predictions.append((product_id, pred.est))

        # Sort by predicted rating and get top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = predictions[:n_recommendations]

        return top_recommendations

    def hybrid_recommendations(self, algo, user_id, n_recommendations=5, alpha=0.5):
        """Generate hybrid recommendations combining content-based and collaborative filtering"""
        logger.info(f"Generating hybrid recommendations for user {user_id}...")

        # Get recommendations from both methods
        content_recs = self.generate_content_based_recommendations(user_id, n_recommendations * 2)
        collab_recs = self.generate_collaborative_recommendations(algo, user_id, n_recommendations * 2)

        # Convert to dictionaries for easier merging
        content_dict = {pid: score for pid, score in content_recs}
        collab_dict = {pid: score for pid, score in collab_recs}

        # Combine scores
        all_products = set(content_dict.keys()) | set(collab_dict.keys())
        hybrid_scores = {}

        for pid in all_products:
            content_score = content_dict.get(pid, 0)
            collab_score = collab_dict.get(pid, 0)

            # Combine scores using weighted average
            hybrid_scores[pid] = alpha * content_score + (1 - alpha) * collab_score

        # Get top N recommendations
        top_recommendations = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]

        return top_recommendations


def main():
    # Initialize database connection
    db_connection = create_engine('postgresql://admin_ecomm:admin_ecomm@postgres:5432/data_warehouse')

    # Initialize recommendation system
    rec_sys = RecommendationSystem(db_connection)

    # Load data
    interactions, products = rec_sys.load_data()

    # Create utility matrix
    utility_matrix = rec_sys.create_utility_matrix(interactions)
    rec_sys.ratings_matrix = utility_matrix

    # Prepare content-based features
    product_features = rec_sys.prepare_content_based_features(products)
    rec_sys.product_features = product_features

    # Start MLflow experiment
    mlflow.set_experiment("Product_Recommendation_System")

    with mlflow.start_run():
        # Run collaborative filtering
        algo, cv_results = rec_sys.collaborative_filtering(interactions)

        # Log metrics
        mlflow.log_metrics({
            "rmse_mean": cv_results['test_rmse'].mean(),
            "mae_mean": cv_results['test_mae'].mean()
        })

        # Generate sample recommendations using different methods
        sample_user = utility_matrix.index[0]

        # Content-based recommendations
        content_recs = rec_sys.generate_content_based_recommendations(sample_user)
        logger.info(f"Content-based recommendations for user {sample_user}: {content_recs}")

        # Collaborative filtering recommendations
        collab_recs = rec_sys.generate_collaborative_recommendations(algo, sample_user)
        logger.info(f"Collaborative recommendations for user {sample_user}: {collab_recs}")

        # Hybrid recommendations
        hybrid_recs = rec_sys.hybrid_recommendations(algo, sample_user)
        logger.info(f"Hybrid recommendations for user {sample_user}: {hybrid_recs}")

        # Log model
        mlflow.sklearn.log_model(algo, 'recommendation_model')

        # Log content-based features
        product_features.to_csv("product_features.csv")
        mlflow.log_artifact("product_features.csv")

        # Register model
        mlflow.register_model(
            "runs:/{}/recommendation_model".format(mlflow.active_run().info.run_id),
            "product_recommendation_model"
        )


if __name__ == "__main__":
    main()