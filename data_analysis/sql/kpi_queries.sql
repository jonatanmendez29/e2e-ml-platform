-- Monthly Revenue Growth
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    SUM(sale_amount) AS monthly_revenue,
    LAG(SUM(sale_amount)) OVER (ORDER BY DATE_TRUNC('month', sale_date)) AS previous_month_revenue,
    ROUND(
        (SUM(sale_amount) - LAG(SUM(sale_amount)) OVER (ORDER BY DATE_TRUNC('month', sale_date))) /
        LAG(SUM(sale_amount)) OVER (ORDER BY DATE_TRUNC('month', sale_date)) * 100, 2
    ) AS growth_rate
FROM sales
GROUP BY DATE_TRUNC('month', sale_date)
ORDER BY month;

-- Customer Lifetime Value (LTV)
WITH customer_revenue AS (
    SELECT
        u.user_id,
        u.name,
        u.country,
        COUNT(s.sale_id) AS total_orders,
        SUM(s.sale_amount) AS total_revenue,
        MIN(s.sale_date) AS first_order_date,
        MAX(s.sale_date) AS last_order_date
    FROM users u
    JOIN sales s ON u.user_id = s.user_id
    GROUP BY u.user_id, u.name, u.country
)
SELECT
    user_id,
    name,
    country,
    total_orders,
    total_revenue,
    ROUND(total_revenue / NULLIF(total_orders, 0), 2) AS avg_order_value,
    first_order_date,
    last_order_date,
    (last_order_date - first_order_date) AS customer_duration_days
FROM customer_revenue
ORDER BY total_revenue DESC;

-- Top Selling Products by Category
SELECT
    p.category,
    p.name AS product_name,
    COUNT(s.sale_id) AS units_sold,
    SUM(s.sale_amount) AS total_revenue,
    ROUND(AVG(s.sale_amount), 2) AS avg_sale_amount
FROM products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.category, p.name
ORDER BY p.category, total_revenue DESC;

-- Customer Acquisition by Month
SELECT
    DATE_TRUNC('month', signup_date) AS signup_month,
    COUNT(user_id) AS new_customers,
    COUNT(DISTINCT country) AS countries_represented
FROM users
GROUP BY DATE_TRUNC('month', signup_date)
ORDER BY signup_month;

-- Sales Performance by Country
SELECT
    u.country,
    COUNT(s.sale_id) AS total_orders,
    SUM(s.sale_amount) AS total_revenue,
    COUNT(DISTINCT u.user_id) AS unique_customers,
    ROUND(SUM(s.sale_amount) / COUNT(DISTINCT u.user_id), 2) AS revenue_per_customer
FROM users u
JOIN sales s ON u.user_id = s.user_id
GROUP BY u.country
ORDER BY total_revenue DESC;