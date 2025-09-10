# End-to-End E-Commerce Analytics & ML Platfrom
An E-Commerce Company's Data Ecosystem

## Project Overview

Build a system that:
1. **Ingests** simulated user and transaction data.
2. **Processes** and stores it in a structured data warehouse.
3. **Analyzes** it to generate business insights.
4. **Trains ML models** for prediction and recommendation.
5. **Serves** predictions via an API.
6. **Evaluates** business decisions with causal inference.
7. **Orchestrates** and **deploys** everything using DevOps/MLOps practices.

## Architecture
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
