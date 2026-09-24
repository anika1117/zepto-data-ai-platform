Zepto Data & AI Platform

This repository contains the three modules developed for the Zepto Data & AI Platform capstone. The project covers data collection and processing, analytics and machine learning, and a document-based support assistant.

Project Structure
zepto-data-ai-platform/
├── data_pipeline/
├── analytics/
├── support_assistant/
├── README.md
├── requirements.txt
└── .gitignore
Setup

Clone the repository and move into the project directory:

git clone <YOUR_REPOSITORY_URL>
cd zepto-data-ai-platform

Create a virtual environment:

python -m venv .venv

On Windows:

.venv\Scripts\activate

Install the dependencies:

pip install -r requirements.txt
Requirements

The project uses one consolidated requirements.txt file for all three modules.

The required Python packages for the data pipeline, analytics module, and support assistant are included in this file, so the dependencies can be installed from the project root.

1. Data Pipeline

The data_pipeline module collects book data from Books to Scrape, cleans the collected data, converts prices from GBP to INR using the required fixed exchange rate, stores the data in a normalized SQLite database, and runs SQL and pandas-based analysis.

Main Components
Web scraping using Requests and BeautifulSoup
Data cleaning and type conversion using pandas
GBP to INR conversion using the fixed rate of 1 GBP = 105.50 INR
Normalized SQLite database
SQL queries for filtering, sorting, limiting, distinct values, ranges, and joins
Equivalent JOIN operation using pandas.merge
Design Decision

Multiple categories are scraped until at least 60 books are collected. The cleaned data is stored in a normalized SQLite database using separate categories and books tables connected through a foreign key.

Running the Data Pipeline

From the project root:

python data_pipeline/pipeline.py

Then create and populate the database:

python data_pipeline/database.py

Run the SQL and pandas analysis:

python data_pipeline/sql_queries.py

The pipeline produces the cleaned book dataset, SQLite database, and query results used for the analysis.

2. Analytics

The analytics module performs exploratory data analysis and machine learning using the Titanic dataset.

Analysis and Models
Dataset inspection
Missing-value analysis
Univariate analysis
Bivariate analysis
Outlier detection using IQR
Correlation analysis
Data visualization
Logistic Regression
Decision Tree
Random Forest
Class-imbalance handling
GridSearchCV
ROC-AUC evaluation
Fare prediction using Linear Regression
Saved preprocessing and modeling pipeline using Joblib
Design Decision

The Titanic dataset is stored locally as titanic.csv so that the analysis can be reproduced without downloading the dataset again. Preprocessing is performed using ColumnTransformer and Pipeline, with transformations fitted only on the training data to avoid data leakage.

Running the Analytics Module

From the project root:

python analytics/analytics.py

This runs the exploratory analysis, preprocessing, model training, evaluation, and regression analysis.

The trained preprocessing and modeling pipeline is also saved using Joblib.

3. Support Assistant

The support_assistant module is a local Zepto policy support assistant. It uses document embeddings, ChromaDB retrieval, LangGraph routing, Pydantic response validation, and FastAPI.

The graded baseline uses deterministic mock responses and does not require an external LLM API key.

Main Components
Fixed Zepto policy document corpus
Local embeddings using all-MiniLM-L6-v2
ChromaDB vector store
Cosine similarity retrieval
LangGraph-based routing
Policy question classification
Top-3 document retrieval
Structured Pydantic response
FastAPI /ask endpoint
Deterministic mock response generation
Design Decision

The assistant uses a deterministic keyword-based intent classifier to separate policy questions from general questions. Policy questions are passed through the ChromaDB retrieval flow, while general questions receive a direct response.

This keeps the graded implementation deterministic and avoids requiring an external LLM service or API key.

Running the Support Assistant

First, ingest the policy documents:

python support_assistant/ingest.py

Then start the FastAPI application:

uvicorn support_assistant.app:app --port 7860

The API will be available at:

http://127.0.0.1:7860

Swagger UI is available at:

http://127.0.0.1:7860/docs
Example Request

Send a POST request to /ask:
```json
{
  "query": "What are Zepto customer support hours?"
}
The response contains:

Answer
Retrieved document sources
Confidence score

Example response structure:
```text
```json
{
  "answer": "Based on the retrieved context: ...",
  "sources": [
    "doc_08",
    "doc_03",
    "doc_06"
  ],
  "confidence": 1.0
}
Docker

The Support Assistant includes a Dockerfile for containerized execution.

Build the image from the project root:

docker build -f support_assistant/Dockerfile -t zepto-support-assistant .

Run the container:

docker run -p 7860:7860 zepto-support-assistant

The application runs on port 7860.

Docker is optional for the local setup. The Support Assistant can also be run directly using Python and Uvicorn as described above.

Overall Design

The project is divided into three independent modules:

Data Pipeline: Collects, cleans, transforms, stores, and queries book data.
Analytics: Performs EDA and machine learning on the Titanic dataset.
Support Assistant: Retrieves information from Zepto policy documents and provides structured answers through a FastAPI service.

Each module has its own implementation and README, while this root README provides the overall project setup and instructions for running the complete capstone.
