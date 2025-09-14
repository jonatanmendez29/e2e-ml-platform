import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
from dowhy import CausalModel
import econml.metalearners as metalearners
from econml.dml import DML
from econml.sklearn_extensions.linear_model import StatsModelsLinearRegression


# Set up logging and plotting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
plt.style.use('seaborn-v0_8')


class MarketingCampaignAnalysis:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.results = {}

    def exploratory_analysis(self):
        """Perform exploratory data analysis"""
        logger.info("Performing exploratory analysis...")

        # Basic statistics
        print("=== BASIC STATISTICS ===")
        print(f"Total users: {len(self.data)}")
        print(f"Treatment group: {self.data['received_email'].sum()}")
        print(f"Control group: {len(self.data) - self.data['received_email'].sum()}")
        print(
            f"Average sales - Treatment: {self.data[self.data['received_email'] == 1]['post_campaign_sales'].mean():.2f}")
        print(
            f"Average sales - Control: {self.data[self.data['received_email'] == 0]['post_campaign_sales'].mean():.2f}")
        print(
            f"Raw difference: {self.data[self.data['received_email'] == 1]['post_campaign_sales'].mean() - self.data[self.data['received_email'] == 0]['post_campaign_sales'].mean():.2f}")

        # Check balance of covariates
        print("\n=== COVARIATE BALANCE ===")
        covariates = ['age', 'total_past_purchases', 'total_past_spend',
                      'days_since_last_purchase', 'email_opens_30d', 'activity_score']

        covariates_list = []
        for covariate in covariates:
            treatment_mean = self.data[self.data['received_email'] == 1][covariate].mean()
            control_mean = self.data[self.data['received_email'] == 0][covariate].mean()
            covariates_list.append({
                'covariate': covariate,
                'treatment_mean': treatment_mean,
                'control_mean': control_mean,
                'difference': treatment_mean - control_mean,
                'std_diff': (treatment_mean - control_mean) / self.data[covariate].std()
            })
        balance_df = pd.DataFrame(covariates_list)
        print(balance_df)

        # Plot distribution of covariates
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for i, covariate in enumerate(covariates):
            sns.histplot(data=self.data, x=covariate, hue='received_email',
                         ax=axes[i], kde=True, alpha=0.6)
            axes[i].set_title(f'Distribution of {covariate}')

        plt.tight_layout()
        plt.savefig('../results/covariate_distributions.png')
        plt.close()

        return balance_df

    def naive_comparison(self):
        """Naive comparison of treatment and control groups"""
        logger.info("Performing naive comparison...")

        # Simple difference in means
        treatment_mean = self.data[self.data['received_email'] == 1]['post_campaign_sales'].mean()
        control_mean = self.data[self.data['received_email'] == 0]['post_campaign_sales'].mean()
        naive_ate = treatment_mean - control_mean

        # Regression adjustment
        model = ols(
            'post_campaign_sales ~ received_email + age + total_past_purchases + total_past_spend + days_since_last_purchase + email_opens_30d + activity_score',
            data=self.data).fit()

        self.results['naive'] = {
            'difference_in_means': naive_ate,
            'regression_adjustment': model.params['received_email'],
            'regression_summary': model.summary()
        }

        print("=== NAIVE COMPARISON ===")
        print(f"Difference in means: {naive_ate:.2f}")
        print(f"Regression adjustment: {model.params['received_email']:.2f}")

        return naive_ate, model

    def propensity_score_matching(self):
        """Perform propensity score matching"""
        logger.info("Performing propensity score matching...")

        # Estimate propensity scores
        covariates = ['age', 'total_past_purchases', 'total_past_spend',
                      'days_since_last_purchase', 'email_opens_30d', 'activity_score']

        X = self.data[covariates]
        y = self.data['received_email']

        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Estimate propensity scores using logistic regression
        ps_model = LogisticRegression()
        ps_model.fit(X_scaled, y)
        self.data['propensity_score'] = ps_model.predict_proba(X_scaled)[:, 1]

        # Plot propensity score distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.data, x='propensity_score', hue='received_email',
                     kde=True, alpha=0.6)
        plt.title('Propensity Score Distribution')
        plt.savefig('../results/propensity_score_distribution.png')
        plt.close()

        # Perform matching (nearest neighbor)
        from sklearn.neighbors import NearestNeighbors

        treatment_df = self.data[self.data['received_email'] == 1]
        control_df = self.data[self.data['received_email'] == 0]

        # Fit nearest neighbors on control group
        nbrs = NearestNeighbors(n_neighbors=1).fit(control_df[['propensity_score']])
        distances, indices = nbrs.kneighbors(treatment_df[['propensity_score']])

        # Create matched dataset
        matched_control = control_df.iloc[indices.flatten()].copy()
        matched_treatment = treatment_df.copy()

        matched_data = pd.concat([matched_treatment, matched_control])

        # Calculate ATE on matched data
        ate_matched = (matched_data[matched_data['received_email'] == 1]['post_campaign_sales'].mean() -
                       matched_data[matched_data['received_email'] == 0]['post_campaign_sales'].mean())

        self.results['psm'] = {
            'ate': ate_matched,
            'treatment_size': len(matched_treatment),
            'control_size': len(matched_control)
        }

        print("=== PROPENSITY SCORE MATCHING ===")
        print(f"ATE (matched): {ate_matched:.2f}")
        print(f"Treatment group size: {len(matched_treatment)}")
        print(f"Control group size: {len(matched_control)}")

        return ate_matched, matched_data

    def difference_in_differences(self):
        """Perform difference-in-differences analysis"""
        logger.info("Performing difference-in-differences analysis...")

        # For DiD, we need pre-treatment and post-treatment data
        # Let's simulate pre-campaign sales data
        np.random.seed(42)
        self.data['pre_campaign_sales'] = np.random.normal(40, 8, len(self.data))

        # Add time trend effect
        self.data['pre_campaign_sales'] += 0.1 * self.data['activity_score']

        # Calculate differences
        self.data['sales_change'] = self.data['post_campaign_sales'] - self.data['pre_campaign_sales']

        # DiD estimate
        treatment_pre = self.data[self.data['received_email'] == 1]['pre_campaign_sales'].mean()
        treatment_post = self.data[self.data['received_email'] == 1]['post_campaign_sales'].mean()
        control_pre = self.data[self.data['received_email'] == 0]['pre_campaign_sales'].mean()
        control_post = self.data[self.data['received_email'] == 0]['post_campaign_sales'].mean()

        did_estimate = (treatment_post - treatment_pre) - (control_post - control_pre)

        # Regression DiD
        self.data['post_period'] = 1  # 1 for post, 0 for pre
        self.data['treatment_group'] = self.data['received_email']

        # Create a panel dataset for DiD
        pre_data = self.data.copy()
        pre_data['post_period'] = 0
        pre_data['sales'] = pre_data['pre_campaign_sales']

        post_data = self.data.copy()
        post_data['post_period'] = 1
        post_data['sales'] = post_data['post_campaign_sales']

        panel_data = pd.concat([pre_data, post_data])

        # DiD regression
        did_model = ols('sales ~ treatment_group + post_period + treatment_group * post_period',
                        data=panel_data).fit()

        self.results['did'] = {
            'simple_did': did_estimate,
            'regression_did': did_model.params['treatment_group:post_period'],
            'regression_summary': did_model.summary()
        }

        print("=== DIFFERENCE-IN-DIFFERENCES ===")
        print(f"Simple DiD estimate: {did_estimate:.2f}")
        print(f"Regression DiD estimate: {did_model.params['treatment_group:post_period']:.2f}")

        return did_estimate, did_model

    def dowhy_analysis(self):
        """Perform causal analysis using DoWhy library"""
        logger.info("Performing DoWhy analysis...")

        # Define causal model
        model = CausalModel(
            data=self.data,
            treatment='received_email',
            outcome='post_campaign_sales',
            common_causes=['age', 'total_past_purchases', 'total_past_spend',
                           'days_since_last_purchase', 'email_opens_30d', 'activity_score']
        )

        # Identify causal effect
        identified_estimand = model.identify_effect()

        # Estimate causal effect
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.propensity_score_matching"
        )

        # Refute estimate
        refutation_results = model.refute_estimate(
            identified_estimand,
            estimate,
            method_name="random_common_cause"
        )

        self.results['dowhy'] = {
            'estimate': estimate.value,
            'refutation': refutation_results
        }

        print("=== DOWHY ANALYSIS ===")
        print(f"Estimated ATE: {estimate.value:.2f}")
        print(f"Refutation test: {refutation_results}")

        return estimate

    def econml_analysis(self):
        """Perform causal analysis using EconML library"""
        logger.info("Performing EconML analysis...")

        # Prepare data
        covariates = ['age', 'total_past_purchases', 'total_past_spend',
                      'days_since_last_purchase', 'email_opens_30d', 'activity_score']

        X = self.data[covariates].values
        T = self.data['received_email'].values
        y = self.data['post_campaign_sales'].values

        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # S-Learner
        s_learner = metalearners.SLearner(overall_model=RandomForestRegressor())
        s_learner.fit(y, T, X=X_scaled)
        s_ate = s_learner.ate(X=X_scaled)

        # T-Learner
        t_learner = metalearners.TLearner(models=LinearRegression())
        t_learner.fit(y, T, X=X_scaled)
        t_ate = t_learner.ate(X=X_scaled)

        # Double Machine Learning
        dml = DML(
            model_y=RandomForestRegressor(),
            model_t=RandomForestClassifier(),
            model_final=StatsModelsLinearRegression(fit_intercept=False),
            discrete_treatment=True
        )
        dml.fit(y, T, X=X_scaled)
        dml_ate = dml.ate(X_scaled)

        self.results['econml'] = {
            's_learner': s_ate,
            't_learner': t_ate,
            'dml': dml_ate
        }

        print("=== ECONML ANALYSIS ===")
        print(f"S-Learner ATE: {s_ate:.2f}")
        print(f"T-Learner ATE: {t_ate:.2f}")
        print(f"DML ATE: {dml_ate:.2f}")

        return s_ate, t_ate, dml_ate

    def run_all_analyses(self):
        """Run all causal analysis methods"""
        logger.info("Running all causal analysis methods...")

        # Create results directory
        import os
        os.makedirs('results', exist_ok=True)

        # Run all analyses
        self.exploratory_analysis()
        self.naive_comparison()
        self.propensity_score_matching()
        self.difference_in_differences()
        self.dowhy_analysis()
        self.econml_analysis()

        # Save results
        results_df = pd.DataFrame({
            'Method': ['Naive Difference', 'Regression Adjustment', 'Propensity Score Matching',
                       'Difference-in-Differences', 'DoWhy', 'S-Learner', 'T-Learner', 'DML'],
            'ATE': [
                self.results['naive']['difference_in_means'],
                self.results['naive']['regression_adjustment'],
                self.results['psm']['ate'],
                self.results['did']['simple_did'],
                self.results['dowhy']['estimate'],
                self.results['econml']['s_learner'],
                self.results['econml']['t_learner'],
                self.results['econml']['dml']
            ]
        })

        results_df.to_csv('../results/causal_analysis_results.csv', index=False)

        # Plot results
        plt.figure(figsize=(12, 8))
        plt.bar(results_df['Method'], results_df['ATE'])
        plt.axhline(y=15, color='r', linestyle='--', label='True ATE (15)')
        plt.xlabel('Method')
        plt.ylabel('Average Treatment Effect')
        plt.title('Comparison of Causal Inference Methods')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig('../results/method_comparison.png')
        plt.close()

        logger.info("All analyses completed. Results saved to results/ directory.")

        return results_df


def main():
    """Main function to run the causal analysis"""
    # Generate data if it doesn't exist
    import os
    if not os.path.exists('../data/marketing_campaign_data.csv'):
        from data_simulation import main as simulate_data
        simulate_data()

    # Run analysis
    analysis = MarketingCampaignAnalysis('../data/marketing_campaign_data.csv')
    results = analysis.run_all_analyses()

    print("\n=== FINAL RESULTS ===")
    print(results)


if __name__ == "__main__":
    main()