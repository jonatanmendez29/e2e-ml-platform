import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection function
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "data_warehouse"),
        user=os.getenv("DB_USER", "admin_ecomm"),
        password=os.getenv("DB_PASSWORD", "admin_ecomm"),
        port=os.getenv("DB_PORT", "5432")
    )

conn = init_connection()

# Helper function to run queries
@st.cache_data(ttl=3600)  # Cache for 1 hour
def run_query(query):
    return pd.read_sql_query(query, conn)

# Dashboard title
st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("## Comprehensive overview of sales performance and customer behavior")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(datetime.now() - timedelta(days=365), datetime.now()),
    max_value=datetime.now()
)

# KPI Metrics
st.subheader("Key Performance Indicators")

# Create columns for KPIs
col1, col2, col3, col4 = st.columns(4)

# Total Revenue
total_revenue = run_query("SELECT SUM(sale_amount) AS total_revenue FROM sales")['total_revenue'].iloc[0]
col1.metric("Total Revenue", f"${total_revenue:,.2f}")

# Total Customers
total_customers = run_query("SELECT COUNT(DISTINCT user_id) AS total_customers FROM sales")['total_customers'].iloc[0]
col2.metric("Total Customers", f"{total_customers:,}")

# Average Order Value
avg_order_value = run_query("SELECT AVG(sale_amount) AS avg_order_value FROM sales")['avg_order_value'].iloc[0]
col3.metric("Average Order Value", f"${avg_order_value:,.2f}")

# Products Sold
total_products = run_query("SELECT COUNT(*) AS total_products FROM sales")['total_products'].iloc[0]
col4.metric("Products Sold", f"{total_products:,}")

# Charts and Visualizations
st.markdown("---")

# Revenue Trend
st.subheader("Monthly Revenue Trend")
revenue_trend = run_query("""
    SELECT 
        DATE_TRUNC('month', sale_date) AS month,
        SUM(sale_amount) AS monthly_revenue
    FROM sales
    GROUP BY DATE_TRUNC('month', sale_date)
    ORDER BY month
""")

fig_revenue = px.line(
    revenue_trend,
    x="month",
    y="monthly_revenue",
    title="Monthly Revenue Over Time",
    labels={"month": "Month", "monthly_revenue": "Revenue ($)"}
)
st.plotly_chart(fig_revenue, use_container_width=True)

# Sales by Category
st.subheader("Sales by Product Category")
sales_by_category = run_query("""
    SELECT 
        p.category,
        SUM(s.sale_amount) AS total_revenue,
        COUNT(s.sale_id) AS total_orders
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
""")

col1, col2 = st.columns(2)

fig_category_revenue = px.pie(
    sales_by_category,
    values="total_revenue",
    names="category",
    title="Revenue by Category"
)
col1.plotly_chart(fig_category_revenue, use_container_width=True)

fig_category_orders = px.bar(
    sales_by_category,
    x="category",
    y="total_orders",
    title="Orders by Category",
    labels={"category": "Category", "total_orders": "Number of Orders"}
)
col2.plotly_chart(fig_category_orders, use_container_width=True)

# Top Products
st.subheader("Top 10 Products by Revenue")
top_products = run_query("""
    SELECT 
        p.name AS product_name,
        p.category,
        SUM(s.sale_amount) AS total_revenue,
        COUNT(s.sale_id) AS units_sold
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.name, p.category
    ORDER BY total_revenue DESC
    LIMIT 10
""")

fig_top_products = px.bar(
    top_products,
    x="product_name",
    y="total_revenue",
    color="category",
    title="Top 10 Products by Revenue",
    labels={"product_name": "Product", "total_revenue": "Revenue ($)"}
)
st.plotly_chart(fig_top_products, use_container_width=True)

# Customer Geography
st.subheader("Customer Distribution by Country")
customers_by_country = run_query("""
    SELECT 
        country,
        COUNT(DISTINCT user_id) AS customer_count
    FROM users
    GROUP BY country
    ORDER BY customer_count DESC
""")

fig_map = px.choropleth(
    customers_by_country,
    locations="country",
    locationmode="country names",
    color="customer_count",
    title="Customer Distribution by Country",
    color_continuous_scale=px.colors.sequential.Plasma
)
st.plotly_chart(fig_map, use_container_width=True)

# Raw Data Explorer
st.subheader("Data Explorer")
table_option = st.selectbox(
    "Select table to view:",
    ["Sales", "Users", "Products"]
)

if table_option == "Sales":
    data = run_query("SELECT * FROM sales LIMIT 100")
elif table_option == "Users":
    data = run_query("SELECT * FROM users LIMIT 100")
else:
    data = run_query("SELECT * FROM products LIMIT 100")

st.dataframe(data)

# Footer
st.markdown("---")
st.markdown("### 📈 E-Commerce Analytics Dashboard")
st.markdown("Built with Streamlit, Plotly, and PostgreSQL")