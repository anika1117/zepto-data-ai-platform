# Zepto Data & AI Platform

This repository contains the three modules developed for the Zepto Data & AI Platform capstone. The project covers data collection and processing, analytics and machine learning, and a document-based support assistant.

## Project Structure
```text
zepto-data-ai-platform/
├── data_pipeline/
├── analytics/
├── support_assistant/
├── README.md
├── requirements.txt
└── .gitignore
```
## Setup
Clone the repository and move into the project directory:

```bash
git clone <YOUR_REPOSITORY_URL>
cd zepto-data-ai-platform
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Requirements

The project uses one consolidated `requirements.txt` file for all three modules.
The required Python packages for the data pipeline, analytics module, and support assistant are included in this file, so the dependencies can be installed from the project root.
---
# 1. Data Pipeline
The `data_pipeline` module implements an end-to-end pipeline for collecting, cleaning, transforming, storing, and querying book data from Books to Scrape.
The pipeline scrapes **69 books across 3 categories** — Travel, Mystery, and Historical Fiction — using Requests and BeautifulSoup. The cleaned data is converted into the required data types, GBP prices are converted to INR using the fixed project rate, and the final data is stored in a normalized SQLite database.

## Main Components

- Web scraping using `requests` and `BeautifulSoup`
- Data cleaning and type conversion using `pandas`
- Price conversion from GBP to INR using the fixed rate of `1 GBP=105.50 INR`
- Normalized SQLite database with `categories` and `books` tables
- SQL queries demonstrating `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `BETWEEN`, `IN`, and `JOIN`
- SQL query results saved in `query_results.txt`
- Equivalent JOIN operation reproduced using `pandas.merge()`

## Data Collection
The scraper collects the following raw fields:
- `title`
- `price`
- `star_rating`
- `availability`
- `category`

The selected categories are:
- Travel
- Mystery
- Historical Fiction
The final scraped dataset contains 69 book records.

## Data Cleaning

The scraped data is transformed into the following cleaned fields:
- `price_gbp`—numeric price after removing the `£` symbol
- `rating`—integer value from 1 to 5 mapped from the star-rating text
- `in_stock`—boolean value parsed from the availability text
- `price_inr`—price converted from GBP to INR
- `category`—category name
Numeric parsing failures are handled using median imputation so that the pipeline does not fail because of missing numeric values. Rows with required fields that remain missing after parsing are removed.

## Currency Conversion
The project uses the required fixed exchange rate:
`1 GBP=105.50 INR`
The INR price is calculated as:

`price_inr=price_gbp * 105.50`

No live currency API is used.

## Database Design

The cleaned data is stored in a normalized SQLite database named `books.db`.

### `categories` table

- `category_id` — Primary Key
- `category_name` — Unique

### `books` table

- `book_id` — Primary Key
- `title`
- `price_gbp`
- `price_inr`
- `rating`
- `in_stock`
- `category_id` — Foreign Key referencing `categories.category_id`

The `category_id` field connects each book with its corresponding category.

## SQL Queries and Validation

Six SQL queries are executed and their SQL statements and outputs are saved in `query_results.txt`.

The queries collectively demonstrate:

- `SELECT` and `WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `BETWEEN`
- `IN`
- `JOIN`

The SQL results are read back into pandas using `pd.read_sql()`.

The `books` and `categories` tables are also loaded into in-memory DataFrames. The SQL JOIN is independently reproduced using `pd.merge()` on `category_id`. Both results are saved in `query_results.txt` and compared for equivalence. The recorded comparison confirms:

`JOIN results match: True`

## Running the Data Pipeline

From the project root, install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the scraping and cleaning pipeline:

```bash
python data_pipeline/pipeline.py
```

Create and populate the SQLite database:

```bash
python data_pipeline/database.py
```

Run the SQL queries and pandas validation:

```bash
python data_pipeline/sql_queries.py
```

## Output Files

The module produces and uses the following files:

- `pipeline.py`—scraping and cleaning pipeline
- `database.py`—SQLite database creation and loading
- `sql_queries.py`—SQL queries and pandas JOIN validation
- `cleaned_books.csv`—cleaned and converted dataset
- `books.db`—normalized SQLite database
- `query_results.txt`—SQL query outputs and JOIN comparison results
- `README.md`—module documentation

## End-to-End Flow

`Books to Scrape → Requests + BeautifulSoup → Data Cleaning → GBP to INR Conversion → cleaned_books.csv → SQLite Database → SQL Queries → pd.read_sql() → pd.merge() JOIN Validation`
---

# 2. Analytics

The `analytics` module performs exploratory data analysis and machine learning using the Titanic dataset.
## Analysis and Models
- Dataset inspection
- Missing-value analysis
- Univariate analysis
- Bivariate analysis
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
- Saved preprocessing and modeling pipeline using Joblib

## Design Decision

The Titanic dataset is loaded using Seaborn in `01_eda.py` and saved as `titanic.csv` for offline reuse. After cleaning, the same CSV is used by `02_modeling.py` for the modeling stage. Preprocessing is performed using `ColumnTransformer` and `Pipeline`, with transformations fitted only on the training data to avoid data leakage.

## Running the Analytics Module

From the project root:

```bash
python analytics/01_eda.py
python analytics/02_modeling.py

```
# 3. Support Assistant

The `support_assistant` module is a local Zepto policy support assistant. It uses document embeddings, ChromaDB retrieval, LangGraph routing, Pydantic response validation, and FastAPI.

The graded baseline uses deterministic mock responses and does not require an external LLM API key.

## Main Components

- Fixed Zepto policy document corpus
- Local embeddings using `all-MiniLM-L6-v2`
- ChromaDB vector store
- Cosine similarity retrieval
- LangGraph-based routing
- Policy question classification
- Top-3 document retrieval
- Structured Pydantic response
- FastAPI `/ask` endpoint
- Deterministic mock response generation

## Design Decision

The assistant uses a deterministic keyword-based intent classifier to separate policy questions from general questions. Policy questions are passed through the ChromaDB retrieval flow, while general questions receive a direct response.

This keeps the graded implementation deterministic and avoids requiring an external LLM service or API key.

## Running the Support Assistant

First, ingest the policy documents:

```bash
python support_assistant/ingest.py
```

Then start the FastAPI application:

```bash
uvicorn support_assistant.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Example Request

Send a POST request to `/ask`:

```json
{
  "query": "How long is Zepto delivery?"
}
```

The response contains:

- Answer
- Retrieved document sources
- Confidence score

## Example Response

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01",
    "doc_08",
    "doc_04"
  ],
  "confidence": 1.0
}
```

General question example:

```json
{
  "query": "What is the capital of India?"
}
```

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

---

# Docker

The Support Assistant includes a Dockerfile for containerized execution.

Build the image from the project root:

```bash
docker build -f support_assistant/Dockerfile -t zepto-support-assistant .
```

Run the container:

```bash
docker run --rm -p 7860:7860 zepto-support-assistant
```

The application runs on port `7860`.

Docker execution was verified successfully. The Docker image built successfully and the container started with Uvicorn on port `7860`.

---

# Overall Design

The project is divided into three independent modules:

- **Data Pipeline:** Collects, cleans, transforms, stores, and queries book data.
- **Analytics:** Performs EDA and machine learning on the Titanic dataset.
- **Support Assistant:** Retrieves information from Zepto policy documents and provides structured answers through a FastAPI service.
Each module has its own implementation and README, while this root README provides the overall project setup and instructions for running the complete capstone.