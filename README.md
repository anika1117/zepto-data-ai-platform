# Zepto Data & AI Platform

This project contains three independent modules built as part of the Zepto Data & AI Platform capstone.

## Modules

### 1. Data Pipeline

The `data_pipeline` module collects book data from Books to Scrape, cleans and transforms the data, converts GBP prices to INR using the required fixed exchange rate, stores the data in a normalized SQLite database, and demonstrates SQL and pandas-based analysis.

Main components:
- Web scraping using Requests and BeautifulSoup
- Data cleaning and type conversion using pandas
- GBP to INR conversion using the fixed rate of 1 GBP = 105.50 INR
- Normalized SQLite database
- SQL queries using filtering, sorting, limiting, distinct values, ranges, and joins
- Equivalent JOIN operation using `pandas.merge`

**Design decision:** Multiple categories are scraped until at least 60 books are collected. Cleaned data is stored in a normalized SQLite schema using categories and books tables linked by a foreign key.

### 2. Analytics

The `analytics` module performs exploratory analysis and machine learning using the Titanic dataset.

It includes:
- Data inspection and missing-value analysis
- Univariate and bivariate analysis
- Outlier detection using IQR
- Correlation analysis
- Data visualization
- Logistic Regression
- Decision Tree
- Random Forest
- Class-imbalance handling
- GridSearchCV
- ROC-AUC evaluation
- Fare prediction using Linear Regression
- Saved complete preprocessing and modeling pipeline using Joblib

**Design decision:** The Titanic dataset is saved locally as `titanic.csv` for offline use. Modeling uses train-only preprocessing through `ColumnTransformer` and `Pipeline` to avoid data leakage.

### 3. Support Assistant

The `support_assistant` module provides a local Zepto policy support service using document embeddings, ChromaDB retrieval, LangGraph routing, structured Pydantic responses, and FastAPI.

The graded baseline uses deterministic mock mode and does not require an LLM API key.

**Design decision:** Policy queries are routed using a deterministic keyword heuristic. Policy queries use ChromaDB retrieval, while general queries use a direct response, keeping the graded baseline deterministic and free of external LLM dependencies.

### Docker

The Support Assistant includes a Dockerfile for local container execution.

The Docker setup uses Uvicorn on port `7860`.

To build the Docker image from the project root:

```bash
docker build -f support_assistant/Dockerfile -t zepto-support-assistant .

To run:

```bash
docker run -p 7860:7860 zepto-support-assistant