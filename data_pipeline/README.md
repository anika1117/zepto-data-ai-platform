# Module 1 — Data Pipeline

## Overview
This module implements an end-to-end data pipeline using `books.toscrape.com`.The pipeline scrapes book data using `requests` and `BeautifulSoup`, cleans and transforms the scraped fields, converts prices from GBP to INR using the project's fixed conversion rate, loads the processed data into a normalized SQLite database, and executes SQL and pandas-based queries.

The pipeline currently produces **69 book records across 3 categories**, satisfying the minimum requirement of 60 books across at least 3 categories.

## Data Source

The data source is [books.toscrape.com](http://books.toscrape.com/), a public website designed for web-scraping practice.

The pipeline uses:

- `requests` for retrieving web pages
- `BeautifulSoup` for parsing the HTML content

No manual copy-pasting is required.

## Scraping

The pipeline scrapes books across multiple categories and follows the category pagination until the available books in the selected categories have been processed.

For each book, the following fields are collected:

- `title`
- `price`
- `star_rating`
- `availability`
- `category`

The final dataset contains 69 book records across 3 categories.

## Data Cleaning

The scraped fields are converted into the required data types before being stored in the database.

### Price

The currency symbol is removed from the scraped price and the value is converted to a floating-point number.

```text
£51.77 → 51.77
```

The cleaned column is:

```text
price_gbp
```

### Star Rating

The text-based star rating is converted to an integer:

```text
One   → 1
Two   → 2
Three → 3
Four  → 4
Five  → 5
```

The cleaned column is:

```text
rating
```

The resulting values are integers from 1 to 5.

### Availability

The scraped availability text is converted into a boolean value.

The cleaned column is:

```text
in_stock
```

### Parsing and Missing-Value Handling

The pipeline is designed to continue processing when numeric fields contain unexpected or unparseable values.

- Unparseable `price_gbp` values are converted to missing values and filled using the median `price_gbp`.
- Unparseable `rating` values are converted to missing values and filled using the median rating.
- Rows with missing required non-numeric fields such as `title` or `category` are dropped because those records cannot be reliably represented in the final dataset.

## Currency Conversion

The project requires a fixed baseline conversion rate:

```text
1 GBP = 105.50 INR
```

This is a project-defined fixed constant and is not a live or historical exchange rate.No currency API or date reference is required.

The `price_inr` column is calculated as:

```text
price_inr = price_gbp × 105.50
```

## Database Design

The processed data is stored in a normalized SQLite database using two related tables:`categories` and `books`.

### `categories`

| Column | Description |
|---|---|
| `category_id` | Primary Key |
| `category_name` | Unique category name |

### `books`

| Column | Description |
|---|---|
| `book_id` | Primary Key |
| `title` | Book title |
| `price_gbp` | Cleaned price in GBP |
| `price_inr` | Converted price in INR |
| `rating` | Integer star rating from 1 to 5 |
| `in_stock` | Boolean stock status |
| `category_id` | Foreign Key referencing `categories.category_id` |

The relationship is:

```text
categories.category_id
        ↑
        |
books.category_id
```

This separates category information from the book records and implements the required primary-key/foreign-key relational structure.

## SQL Queries

Six SQL queries are executed against the SQLite database.

Collectively, the queries demonstrate:

- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `BETWEEN`
- `IN`
- `JOIN`

The executed query strings and their outputs are saved in:

```text
query_results.txt
```

The JOIN query combines the `books` and `categories` tables using `category_id`.

## Pandas Validation

SQL query results are read back into pandas using `pd.read_sql()`.

The database `books` and `categories` data are also loaded into in-memory DataFrames.The SQL JOIN is independently reproduced using:

```text
pd.merge()
```

The merge is performed using `category_id`.

The SQL JOIN result and the pandas merge result are compared for equivalence. Both results are saved in `query_results.txt`, and the comparison confirms that they match.

## Pipeline Execution

From the repository root, install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the data pipeline:

```bash
python data_pipeline/pipeline.py
```

Create/load the SQLite database:

```bash
python data_pipeline/database.py
```

Execute the SQL queries and pandas validation:

```bash
python data_pipeline/sql_queries.py
```

## Output Files

The `data_pipeline` module produces and contains the following key outputs:

```text
data_pipeline/
├── pipeline.py
├── database.py
├── sql_queries.py
├── cleaned_books.csv
├── books.db
├── query_results.txt
└── README.md
```

### `cleaned_books.csv`

Contains the cleaned and converted book data, including:

- `title`
- `price_gbp`
- `rating`
- `in_stock`
- `category`
- `price_inr`

### `books.db`

SQLite database containing the normalized `categories` and `books` tables.

### `query_results.txt`

Contains the executed SQL query strings, their outputs, the pandas merge output, and the SQL JOIN versus pandas merge comparison.

## End-to-End Flow
```text
books.toscrape.com
        ↓
requests + BeautifulSoup
        ↓
Scraped book data
        ↓
Data cleaning
        ↓
Median imputation / required-field handling
        ↓
GBP → INR conversion
        ↓
SQLite normalized database
        ↓
SQL queries
        ↓
pd.read_sql()
        ↓
pd.merge()
        ↓
SQL JOIN validation
```