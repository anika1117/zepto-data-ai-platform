import sqlite3
import pandas as pd

DB_PATH = "data_pipeline/books.db"
OUTPUT_PATH = "data_pipeline/query_results.txt"


queries = {
    "Query 1 - WHERE": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
    """,

    "Query 2 - ORDER BY and LIMIT": """
        SELECT title, price_inr
        FROM books
        ORDER BY price_inr DESC
        LIMIT 10
    """,

    "Query 3 - DISTINCT": """
        SELECT DISTINCT rating
        FROM books
        ORDER BY rating
    """,

    "Query 4 - BETWEEN": """
        SELECT title, price_gbp
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp
    """,

    "Query 5 - IN": """
        SELECT title, rating, category_id
        FROM books
        WHERE rating IN (4, 5)
    """,

    "Query 6 - JOIN": """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            b.rating,
            c.category_name
        FROM books b
        JOIN categories c
        ON b.category_id = c.category_id
        ORDER BY b.book_id
        LIMIT 10
    """
}


def main():
    connection = sqlite3.connect(DB_PATH)

    output = []

    for name, query in queries.items():
        result = pd.read_sql(query, connection)

        output.append(name)
        output.append("SQL:")
        output.append(query.strip())
        output.append("Output:")
        output.append(result.to_string(index=False))
        output.append("\n" + "=" * 80 + "\n")

    books_df = pd.read_sql(
        """
        SELECT book_id, title, price_gbp, rating, in_stock, category_id
        FROM books
        """,
        connection
    )

    categories_df = pd.read_sql(
        """
        SELECT category_id, category_name
        FROM categories
        """,
        connection
    )

    merge_result = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    merge_result = merge_result[
        [
            "book_id",
            "title",
            "price_gbp",
            "rating",
            "category_name"
        ]
    ].sort_values("book_id").head(10)

    sql_join_result = pd.read_sql(
    queries["Query 6 - JOIN"],
    connection
)
    join_matches = sql_join_result.equals(
    merge_result.reset_index(drop=True)
)
    output.append("PANDAS MERGE - JOIN REPRODUCTION")
    output.append("Output:")
    output.append(merge_result.to_string(index=False))
    output.append(f"JOIN results match: {join_matches}")
    output.append("\n" + "=" * 80 + "\n")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(output))

    print("SQL queries executed successfully.")
    print("Results saved to:", OUTPUT_PATH)
    print("\nSQL JOIN result:")
    print(sql_join_result)

    print("\nPandas merge result:")
    print(merge_result)

    print(
    "\nJOIN results match:",
    sql_join_result.equals(merge_result.reset_index(drop=True))
    )

    connection.close()


if __name__ == "__main__":
    main()