import pandas as pd
import numpy as np
from faker import Faker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_marketing_campaign_data(n_users=5000, campaign_date='2025-06-01'):
    """
    Simulate data for a marketing email campaign evaluation
    Includes confounders, treatment assignment, and outcomes
    """
    np.random.seed(42)
    fake = Faker(['es_MX', 'en_US', 'en_GB'])

    # Create user base
    users = []
    for i in range(n_users):
        signup_date = fake.date_between(start_date='-2y', end_date='-30d')
        users.append({
            "user_id": i + 1,
            "age": np.random.randint(18, 70),
            "country": fake.current_country(),
            "signup_date": signup_date,
            "total_past_purchases": np.random.poisson(5),
            "total_past_spend": np.random.gamma(100, 2),
            "days_since_last_purchase": np.random.randint(1, 180),
            "email_opens_30d": np.random.poisson(3),
            # These are confounders that affect both treatment and outcome
            "activity_score": np.random.normal(50, 15)
        })

    users_df = pd.DataFrame(users)

    # Simulate treatment assignment (who received the marketing email)
    # Treatment probability depends on confounders (non-random assignment)
    users_df['treatment_prob'] = 1 / (1 + np.exp(-(users_df['activity_score'] - 50) / 10))
    users_df['received_email'] = np.random.binomial(1, users_df['treatment_prob'])

    # Remove the probability column
    users_df = users_df.drop('treatment_prob', axis=1)

    # Simulate outcomes (sales after campaign)
    # Base sales + treatment effect + confounder effects
    base_sales = np.random.normal(50, 10, n_users)
    treatment_effect = 15  # True average treatment effect
    confounder_effect = 0.5 * users_df['activity_score']

    users_df['post_campaign_sales'] = (
            base_sales +
            treatment_effect * users_df['received_email'] +
            confounder_effect +
            np.random.normal(0, 5, n_users)  # Random noise
    )

    # Ensure no negative sales
    users_df['post_campaign_sales'] = users_df['post_campaign_sales'].clip(lower=0)

    # Add campaign date
    users_df['campaign_date'] = campaign_date

    logger.info(f"Simulated data for {n_users} users")
    logger.info(f"Treatment group size: {users_df['received_email'].sum()}")
    logger.info(f"Control group size: {len(users_df) - users_df['received_email'].sum()}")

    return users_df


def main():
    """Generate and save simulated data"""
    data = simulate_marketing_campaign_data()
    data.to_csv('../data/marketing_campaign_data.csv', index=False)
    logger.info("Data saved to data/marketing_campaign_data.csv")


if __name__ == "__main__":
    main()