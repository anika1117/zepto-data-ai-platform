import sqlite3
import pandas as pd

DB_PATH = "data_pipeline/books.db"
CSV_PATH = "data_pipeline/cleaned_books.csv"


def create_database():
    df = pd.read_csv(CSV_PATH)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute("""
        DROP TABLE IF EXISTS books
    """)

    connection.execute("""
        DROP TABLE IF EXISTS categories
    """)

    connection.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT UNIQUE NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id)
            REFERENCES categories(category_id)
        )
    """)

    categories = df["category"].drop_duplicates().tolist()

    for category_id, category_name in enumerate(categories, start=1):
        connection.execute(
            "INSERT INTO categories (category_id, category_name) VALUES (?, ?)",
            (category_id, category_name)
        )

    category_map = dict(
        connection.execute(
            "SELECT category_name, category_id FROM categories"
        ).fetchall()
    )

    for _, row in df.iterrows():
        connection.execute(
            """
            INSERT INTO books
            (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                row["price_gbp"],
                row["price_inr"],
                row["rating"],
                int(row["in_stock"]),
                category_map[row["category"]]
            )
        )

    connection.commit()

    print("Database created successfully.")
    print("Categories:", len(categories))
    print("Books:", len(df))

    print("\nCategories:")
    print(pd.read_sql("SELECT * FROM categories", connection))

    print("\nBooks:")
    print(pd.read_sql("SELECT * FROM books LIMIT 5", connection))

    connection.close()


if __name__ == "__main__":
    create_database()