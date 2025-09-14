# PersonaBank-AI: Customer Analytics & Fraud Detection

This project aims to build a comprehensive customer analytics platform by integrating multiple banking and financial datasets. The end goal is to enable advanced customer segmentation and develop a machine learning model for fraud detection.

The current version completes **Phase 1**, which establishes the foundational data environment.

## Tech Stack

-   **Containerization**: Docker & Docker Compose
-   **Database**: PostgreSQL
-   **Data Ingestion**: Python, pandas, psycopg2
-   **Security**: `dotenv` for environment variable management

## Current Status: Phase 1 Complete

-   [x] **Containerized Environment**: A reproducible PostgreSQL database is defined in `docker-compose.yml`.
-   [x] **Secure Configuration**: Database credentials are kept out of version control using a `.env` file.
-   [x] **Automated Data Ingestion**: A Python script (`load_data.py`) automatically loads all raw CSV files into the database.
-   [x] **Data Loaded**: Four key datasets covering customer profiles, marketing, and transactions have been successfully ingested.

## Getting Started

### Prerequisites

-   Docker Desktop
-   Python 3.8+

### Setup

1.  **Clone the Repository**
    ```
    git clone https://github.com/your-username/PersonaBank-AI.git
    cd PersonaBank-AI
    ```

2.  **Set Up Environment File**
    Create a `.env` file in the project root:
    ```
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_DB=banking_analytics
    ```

3.  **Start the Database**
    This command starts the PostgreSQL container.
    ```
    docker-compose up -d
    ```

4.  **Install Dependencies**
    ```
    pip install pandas psycopg2-binary python-dotenv
    ```

5.  **Download and Load Data**
    -   Create a `data` folder in the project root.
    -   Download the required CSV files and place them in the `data` folder.
    -   Run the ingestion script:
        ```
        python3 load_data.py
        ```

The environment is now set up with all raw data loaded and ready for Phase 2.
