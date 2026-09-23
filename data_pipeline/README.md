# Module 1 — Data Pipeline

## Overview

This module scrapes book data from `books.toscrape.com`, cleans and converts the data, stores it in a normalized SQLite database, and demonstrates SQL and pandas queries.

## Run

From the repository root:

```bash
python data_pipeline/pipeline.py
python data_pipeline/database.py
python data_pipeline/sql_queries.py

## Pipeline

1. Scrapes books from multiple categories until at least 60 books are collected.
2. Collects title, price, star rating, availability, and category.
3. Cleans the data:
   - `price_gbp` → float
   - `rating` → integer 1–5
   - `in_stock` → boolean
4. Rows missing required fields are removed.
5. Currency conversion uses the fixed rate:

`1 GBP = 105.50 INR`

6. Saves cleaned data to `cleaned_books.csv`.
7. Creates a normalized SQLite database with `categories` and `books` tables.
8. Runs SQL queries and saves outputs to `query_results.txt`.

## Database Design

### categories

- `category_id` — Primary Key
- `category_name` — Unique

### books

- `book_id` — Primary Key
- `title`
- `price_gbp`
- `price_inr`
- `rating`
- `in_stock`
- `category_id` — Foreign Key referencing `categories`

## SQL and Pandas

The SQL queries demonstrate:

- SELECT / WHERE
- ORDER BY
- LIMIT
- DISTINCT
- BETWEEN
- IN
- JOIN

Query results are loaded using `pd.read_sql`.

The SQL JOIN is also reproduced using `pd.merge()` directly on in-memory DataFrames.

## Output Files

- `cleaned_books.csv`
- `books.db`
- `query_results.txt`