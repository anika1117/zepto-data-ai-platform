import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


BASE_URL = "https://books.toscrape.com/"
MIN_BOOKS = 60
MIN_CATEGORIES = 3


def get_soup(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def get_categories():
    soup = get_soup(BASE_URL)
    categories = []

    for link in soup.select("ul.nav-list ul li a"):
        categories.append({
            "name": link.get_text(strip=True),
            "url": urljoin(BASE_URL, link.get("href"))
        })

    return categories


def scrape_category(category_name, category_url):
    books = []
    current_url = category_url

    while current_url:
        print(f"Scraping: {current_url}")

        soup = get_soup(current_url)

        for product in soup.select("article.product_pod"):
            title_tag = product.select_one("h3 a")
            price_tag = product.select_one("p.price_color")
            rating_tag = product.select_one("p.star-rating")
            availability_tag = product.select_one("p.availability")

            title = title_tag.get("title", "").strip() if title_tag else None
            price = price_tag.get_text(strip=True) if price_tag else None

            star_rating = None
            if rating_tag:
                for value in ["One", "Two", "Three", "Four", "Five"]:
                    if value in rating_tag.get("class", []):
                        star_rating = value
                        break

            availability = (
                availability_tag.get_text(" ", strip=True)
                if availability_tag else None
            )

            books.append({
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category_name
            })

        next_button = soup.select_one("li.next a")

        if next_button:
            current_url = urljoin(current_url, next_button.get("href"))
        else:
            current_url = None

    return books


def clean_data(df):
    df["price_gbp"] = pd.to_numeric(
        df["price"].str.replace(r"[^\d.]", "", regex=True),
        errors="coerce"
    )

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    df["rating"] = df["star_rating"].map(rating_map)

    df["in_stock"] = df["availability"].str.contains(
        "In stock",
        case=False,
        na=False
    )

    df = df.dropna(
        subset=[
            "title",
            "price_gbp",
            "rating",
            "in_stock",
            "category"
        ]
    ).copy()

    df["price_inr"] = df["price_gbp"] * 105.50

    return df


def main():
    print("Finding categories...")

    categories = get_categories()

    print(f"Total categories found: {len(categories)}")

    all_books = []
    categories_used = []

    for category in categories:
        print(f"\nStarting category: {category['name']}")

        books = scrape_category(
            category["name"],
            category["url"]
        )
        all_books.extend(books)
        categories_used.append(category["name"])

        print(f"Books collected so far: {len(all_books)}")

        if len(categories_used) >= MIN_CATEGORIES and len(all_books) >= MIN_BOOKS:
            break

    df = pd.DataFrame(all_books)

    print("\nRaw rows:", len(df))
    print("Categories:", df["category"].nunique())

    df = clean_data(df)

    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]

    print("\nCleaned dataset:")
    print(df.head())

    print("\nFinal shape:", df.shape)

    print("\nCategories:")
    print(df["category"].unique())

    print("\nData types:")
    print(df.dtypes)
    assert len(df) >= MIN_BOOKS
    assert df["category"].nunique() >= MIN_CATEGORIES
    assert df["price_gbp"].dtype.kind == "f"
    assert df["rating"].between(1, 5).all()
    assert df["in_stock"].dtype == bool
    assert df["price_inr"].notna().all()

    df.to_csv(
        "data_pipeline/cleaned_books.csv",
        index=False
    )

    print("\nSaved: data_pipeline/cleaned_books.csv")


if __name__ == "__main__":
    main()