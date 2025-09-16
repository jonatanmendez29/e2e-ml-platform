# End-to-End E-Commerce Analytics & ML Platfrom
# 🎯 Project Overview
Welcome to my comprehensive **E-Commerce Machine Learning Platform** - a full-stack data science project that demonstrates modern data engineering, machine learning, and cloud deployment practices. 
This platform simulates a real-world e-commerce ecosystem, transforming raw data into actionable business intelligence through a complete ML pipeline.

## What This Project Solves
In today's data-driven world, businesses need more than just isolated models—they need integrated systems that can collect, process, analyze, and serve predictions at scale. This project addresses that need by providing:

- 📊 **Data Engineering Foundation**: Robust pipelines that ensure data quality and reliability

- 🤖 **Machine Learning Operations**: Production-ready models with proper tracking and versioning

- 📈 **Business Intelligence**: Interactive dashboards for data-driven decision making

- ⚡ **API Deployment**: Scalable services that make predictions accessible to applications

- 🔍 **Causal Analysis**: Advanced statistical methods to measure true business impact

## Key Value Propositions
- **End-to-End Integration**: From data generation to business insights in one cohesive system
- **Production-Ready Architecture**: Built with industry best practices and scalability in mind
- **MLOps Excellence**: Comprehensive model tracking, versioning, and deployment strategies
- **Real-World Relevance**: Solves practical business problems like customer churn and product recommendations
- **Learning Showcase**: Demonstrates proficiency across the entire data science stack

## 🏗️ System Architecture
### Local Development Architecture
```mermaid
graph TB
    subgraph "Local Development Environment"
        A[Data Generation Scripts<br/>Faker/Python] -->|CSV Files| B[Apache Airflow<br/>Docker Container]
        B -->|Orchestrates| C[Data Quality Checks<br/>pandas assertions]
        C -->|Validated Data| D[PostgreSQL<br/>Docker Container]
        D -->|Stores Data| E[(Data Warehouse<br/>Star Schema)]
        E -->|Query Data| F[Streamlit Dashboard<br/>Docker Container]
        F -->|Visualizations| G[Web Browser<br/>localhost:8501]
        
        B -->|Metadata| H[Airflow Metadata DB<br/>PostgreSQL]
        
        style A fill:#e1f5fe
        style B fill:#fff3e0
        style C fill:#f1f8e9
        style D fill:#ffebee
        style E fill:#f3e5f5
        style F fill:#e8f5e9
        style G fill:#e0f2f1
        style H fill:#fff8e1
    end
```
### AWS Deployment Architecture
```mermaid
graph TB
    subgraph "AWS Cloud Environment"
        subgraph "Data Generation & Orchestration"
            A[Airflow ECS Task<br/>or MWAA] -->|Generates Data| B[AWS S3<br/>Raw Data Lake]
            A -->|Orchestrates| C[AWS Lambda<br/>Data Processing]
        end
        
        subgraph "Data Storage"
            B -->|Stores Raw Data| D[AWS S3<br/>Processed Data]
            C -->|Processes Data| D
            D -->|Loads Data| E[AWS Redshift/RDS<br/>Data Warehouse]
        end
        
        subgraph "Analysis & Visualization"
            E -->|Query Data| F[Streamlit App<br/>ECS Fargate]
            F -->|Serves Dashboard| G[Application Load Balancer]
            G -->|Web Interface| H[End Users<br/>Web Browser]
        end
        
        subgraph "ML Serving"
            E -->|Features| I[SageMaker Endpoint<br/>or ECS Service]
            I -->|Predictions| J[API Gateway]
            J -->|Serves API| K[Client Applications]
        end
        
        subgraph "Infrastructure Management"
            L[Terraform<br/>Infrastructure as Code] --> M[AWS CloudFormation<br/>Resource Management]
            N[GitHub Actions<br/>CI/CD] --> O[ECR<br/>Container Registry]
            O -->|Deploys Images| F
            O -->|Deploys Images| I
        end
        
        style A fill:#fff3e0
        style B fill:#bbdefb
        style C fill:#c8e6c9
        style D fill:#b3e5fc
        style E fill:#d1c4e9
        style F fill:#c5e1a5
        style G fill:#80deea
        style H fill:#e0f2f1
        style I fill:#ffcc80
        style J fill:#ce93d8
        style K fill:#f48fb1
        style L fill:#ef9a9a
        style M fill:#bcaaa4
        style N fill:#9fa8da
        style O fill:#90caf9
    end
    
    P[External Data Sources] -->|Data Ingestion| A
```
### Data Pipeline Flow
```mermaid
flowchart TD
    A[Data Generation<br/>Faker Scripts] --> B[Raw Data Storage<br/>CSV Files]
    B --> C[Data Validation<br/>pandas assertions]
    C --> D[Data Transformation<br/>SQL/Python]
    D --> E[Data Warehouse<br/>PostgreSQL Star Schema]
    E --> F[Business Intelligence<br/>Streamlit Dashboard]
    E --> G[Machine Learning<br/>Feature Engineering]
    G --> H[Model Training<br/>MLflow Tracking]
    H --> I[Model Registry<br/>MLflow Registry]
    I --> J[Model Serving<br/>FastAPI]
    J --> K[Predictions<br/>REST API]
    
    style A fill:#e1f5fe
    style B fill:#bbdefb
    style C fill:#c8e6c9
    style D fill:#fff9c4
    style E fill:#d1c4e9
    style F fill:#c5e1a5
    style G fill:#ffcc80
    style H fill:#ffab91
    style I fill:#f8bbd0
    style J fill:#ce93d8
    style K fill:#b39ddb
```
### DevOps/MLOps Workflow
```mermaid
flowchart LR
    A[Code Changes<br/>GitHub Repository] --> B[CI/CD Pipeline<br/>GitHub Actions]
    B --> C[Run Tests<br/>pytest]
    C --> D[Build Containers<br/>Docker]
    D --> E[Push to Registry<br/>ECR]
    E --> F[Deploy to AWS<br/>Terraform]
    F --> G[Infrastructure Provisioning<br/>AWS Resources]
    G --> H[Service Deployment<br/>ECS/SageMaker]
    H --> I[Monitoring<br/>CloudWatch]
    I --> J[Logging & Alerts<br/>SNS]
    J --> K[Performance Optimization<br/>Feedback Loop]
    K --> A
    
    style A fill:#e1f5fe
    style B fill:#ffecb3
    style C fill:#c8e6c9
    style D fill:#bbdefb
    style E fill:#d1c4e9
    style F fill:#ffcc80
    style G fill:#c5e1a5
    style H fill:#f8bbd0
    style I fill:#ce93d8
    style J fill:#b39ddb
    style K fill:#ef9a9a
```
### Technology Stack Diagram
```mermaid
graph TB
    subgraph "Programming Languages"
        A[Python<br/>Data Processing]
        B[SQL<br/>Data Analysis]
    end
    
    subgraph "Data Engineering"
        C[Apache Airflow<br/>Orchestration]
        D[PostgreSQL<br/>Data Warehouse]
        E[pandas<br/>Data Manipulation]
    end
    
    subgraph "ML Engineering"
        F[MLflow<br/>Experiment Tracking]
        G[Scikit-learn<br/>Model Training]
        H[FastAPI<br/>Model Serving]
    end
    
    subgraph "DevOps/MLOps"
        I[Docker<br/>Containerization]
        J[Terraform<br/>Infrastructure as Code]
        K[GitHub Actions<br/>CI/CD]
    end
    
    subgraph "Cloud Services"
        L[Amazon S3<br/>Data Lake]
        M[Amazon RDS/Redshift<br/>Data Warehouse]
        N[Amazon ECS<br/>Container Orchestration]
        O[Amazon SageMaker<br/>ML Platform]
    end
    
    A --> C
    B --> D
    E --> F
    F --> G
    G --> H
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    
    style A fill:#e1f5fe
    style B fill:#ffecb3
    style C fill:#c8e6c9
    style D fill:#bbdefb
    style E fill:#d1c4e9
    style F fill:#ffcc80
    style G fill:#c5e1a5
    style H fill:#f8bbd0
    style I fill:#ce93d8
    style J fill:#b39ddb
    style K fill:#ef9a9a
    style L fill:#a5d6a7
    style M fill:#ffe082
    style N fill:#90caf9
    style O fill:#f48fb1
```
## ✨ Key Features
### 🔄 Data Engineering Excellence
- Automated data pipelines with Apache Airflow
- Data quality validation with pandas assertions
- PostgreSQL data warehouse with star schema design
- Data version control and lineage tracking

### 🤖 Intelligent Machine Learning
- **Customer Churn Prediction**: Identify at-risk customers with 85%+ accuracy
- **Product Recommendation System**: Collaborative filtering for personalized suggestions
- **MLflow Integration**: Complete experiment tracking and model registry
- **Hyperparameter Optimization**: Automated model tuning for best performance

### 📊 Actionable Business Insights
- Interactive Streamlit dashboard with real-time metrics
- Customer lifetime value analysis
- Sales performance tracking by category and geography
- Exportable reports for business stakeholders

### ⚡ Production-Grade APIs
- RESTful FastAPI services with OpenAPI documentation
- Model serving endpoints for real-time predictions
- Comprehensive testing suite with pytest
- Docker containerization for easy deployment

### 🔍 Advanced Causal Analysis
- Propensity Score Matching for treatment effect estimation
- Difference-in-Differences for longitudinal analysis
- Econometric methods to measure true campaign impact
- Jupyter notebooks for reproducible research

### 🛠️ Technology Stack
- **Data Engineering**: Apache Airflow, PostgreSQL, pandas, SQLAlchemy 
- **Machine Learning**: Scikit-learn, MLflow, Surprise, XGBoost
- **Visualization**: Streamlit, Plotly, Matplotlib, Seaborn
- **API Development**: FastAPI, Pydantic, Uvicorn
- **Causal Analysis**: DoWhy, EconML, Statsmodels
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Cloud Ready**: Terraform, AWS ECS, S3, RDS

## 🎯 Learning Outcomes
Through this project, I've developed and demonstrated expertise in:
- Building scalable data pipelines with proper error handling
- Implementing MLOps practices for reproducible machine learning
- Creating production-ready API services with comprehensive testing
- Designing interactive dashboards for business intelligence
- Applying causal inference methods to measure real business impact
- Containerizing applications for consistent development and deployment
- Preparing systems for cloud deployment with infrastructure as code

This project represents my commitment to building complete, production-ready data solutions that solve real business problems. It's been an incredible journey through the entire data science stack, and I'm excited to apply these skills to new challenges!

***Explore the code, run the system locally, or deploy to AWS—everything you need is in the documentation below. Let's build the future of data-driven decision making together!*** 🚀

# Local Development Setup
Follow these step-by-step instructions to set up and run the complete E-Commerce ML Platform on your local machine.

## 🛠️ Prerequisites
Before you begin, ensure you have the following installed:
- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git (for cloning the repository)
- At least 8GB RAM and 20GB free disk space

## 📥 Step 1: Clone and Setup the Project
```Shell
# Clone the repository
git clone git@github.com:jonatanmendez29/e2e-ml-platform.git
cd e2e-ml-platform

# Create environment file
cp .env.example .env
```

The .env has:
```text
# Database
POSTGRES_DB=data_warehouse
POSTGRES_USER=admin_ecomm
POSTGRES_PASSWORD=admin_ecomm

# Airflow
AIRFLOW_UID=20000
AIRFLOW_GID=20000

# MLflow
MLFLOW_ARTIFACT_ROOT=/mlflow/artifacts

# Streamlit
STREAMLIT_SERVER_PORT=8501

# FastAPI
FASTAPI_PORT=8000

# Jupyter
JUPYTER_PORT=8888
```
## 🐳 Step 2: Start the Database Services
```Shell
# Start only PostgreSQL first to initialize databases
docker compose up -d postgres

# Wait for PostgreSQL to be ready (about 30 seconds)
sleep 30

# Verify database initialization
docker compose exec postgres psql -U admin_ecomm -l
```
You should see three databases: `airflow_metadata`, `mlflow_tracking`, and `data_warehouse`.

## 🔄 Step 3: Initialize Airflow Database
```Shell
# Initialize Airflow database
docker compose run airflow-cli airflow config list
docker compose up airflow-init
```
After initialization is complete, you should see a message like this:

```Shell
airflow-init_1       | Upgrades done
airflow-init_1       | Admin user admin_ecomm created
airflow-init_1       | 3.0.6
start_airflow-init_1 exited with code 0
```

After that you need to stop all services or even delete services and volumes for a fresh start.
```Shell
docker compose down #just stop all services
docker compose down --volumes --remove-orphans
```
## 🚀 Step 4: Start All Services

```Shell
# Start all services
docker-compose up -d 

# Check all services are running
docker-compose ps
```
Wait for all services to start (2-3 minutes). You should see all services in "running" state.

## ✅ Step 5: Verify Services are Accessible
Check that each service is working by accessing them in your browser:

1. Airflow - http://localhost:8080
   - Username: admin 
   - Password: admin 
   - You should see the Airflow DAGs interface
2. Streamlit Dashboard - http://localhost:8501
   - Should show the e-commerce analytics dashboard
3. MLFlow - http://localhost:5050
   - Should show the MLFlow experiment tracking interface
4. FastAPI Documentation - http://localhost:8000/docs
   - Should show interactive API documentation
5. Jupyter Notebook - http://localhost:8888
   - Should show JupyterLab interface

## 📊 Step 6: Generate and Load Sample Data
```Shell
# Run the data generation pipeline in Airflow
# 1. Go to http://localhost:8080
# 2. Login with admin_ecomm/admin_ecomm
# 3. Find the 'ecommerce_data_pipeline' DAG
# 4. Click the play button to trigger the DAG
# 5. Wait for all tasks to complete (green status)

# Alternatively, run data generation manually
docker compose exec airflow-webserver python /opt/airflow/scripts/data_generator.py
```
## 🤖 Step 7: Train Machine Learning Models
```Shell
# Train the churn prediction model
docker compose exec mlflow python churn_prediction/main.py

# Train the recommendation model
docker compose exec mlflow python recommendation/main.py
```
After training, refresh http://localhost:5050 to see your models in MLFlow.

## 🧪 Step 8: Test the API Endpoints
```Shell
# Test churn prediction API
curl -X POST "http://localhost:8000/predict/churn" \
  -H "Content-Type: application/json" \
  -d '{
    "users": [
      {
        "user_id": 1,
        "age": 35,
        "country": "United States",
        "total_orders": 10,
        "total_spent": 500.0,
        "days_since_last_order": 15,
        "avg_order_value": 50.0,
        "customer_duration_days": 365,
        "order_frequency": 0.0274,
        "daily_spend": 1.37
      }
    ]
  }'

# Test health endpoint
curl http://localhost:8000/health
```

## 🔍 Step 9: Run Causal Analysis
1. Open http://localhost:8888
2. Navigate to the causal-analysis/notebooks directory 
3. Open and run the causal analysis notebook

## 🛑 Step 10: Stopping the Services
```Shell
# Stop all services (preserve data)
docker compose down

# Stop and remove all data
docker compose down -v
```

## 🔧 Troubleshooting Common Issues
### Port Conflicts
If ports are already in use, change them in your .env file:
```Shell
# Update these values in your .env
AIRFLOW_PORT=8080
STREAMLIT_PORT=8501
MLFLOW_PORT=5050
FASTAPI_PORT=8000
JUPYTER_PORT=8888
```

### Database Connection Issues
```Shell
# Check if PostgreSQL is running
docker-compose logs postgres

# Reset databases if needed
docker-compose down -v
docker-compose up -d postgres
sleep 30
docker-compose up -d
```

### Out of Memory Errors
```Shell
# Increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory (≥ 8GB)

# Or limit services memory in docker-compose.yml
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 2G
```
### Service Health Checks
```Shell
# Check service logs
docker compose logs airflow-webserver
docker compose logs mlflow
docker compose logs fastapi

# Check individual service health
docker compose exec postgres pg_isready
curl http://localhost:8000/health
```
<div align="center" style="overflow-x: auto; white-space: nowrap;"> 
    <img src="/screenshots/Airflow.jpeg" alt="Airflow Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;"> 
    <img src="/screenshots/Airflow _dag.jpeg" alt="Airflow Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
    <img src="/screenshots/Airflow_dag_exe.jpeg" alt="Airflow Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
    <img src="/screenshots/Airflow_dag_succ.jpeg" alt="Airflow Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
    <img src="/screenshots/Dashboard.jpeg" alt="Streamlit Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
    <img src="/screenshots/Dashboard_2.jpeg" alt="Streamlit Dashboard" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
    <img src="/screenshots/MLflow.jpeg" alt="MLFlow Experiments" width="300" style="display: inline-block; margin: 5px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
</div>

# 📝 Next Steps
After successful setup:
1. **Explore the Data**: Check the Streamlit dashboard at http://localhost:8501
2. **Run Experiments**: Use MLFlow at http://localhost:5050 to track new experiments 
3. **Test APIs**: Use the FastAPI docs at http://localhost:8000/docs
4. **Modify Code**: The code is mounted in containers, so changes will reflect immediately 
5. **Add New Features**: Extend the platform with new models or analyses

# 🆘 Getting Help
If you encounter issues:
1. Check the service logs: docker compose logs <service-name>
2. Verify all containers are running: docker-compose ps 
3. Ensure databases are initialized: Check PostgreSQL logs 
4. Check the troubleshooting section above

The platform is now ready for development and experimentation! 🎉
