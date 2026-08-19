from pathlib import Path

import pandas as pd
from sqlalchemy import select

from backend.database.database import SessionLocal
from backend.database.models import Product, Sale


ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "enriched_pricing_dataset.csv"
)

PRODUCTS_PATH = (
    ROOT
    / "data"
    / "raw"
    / "products.csv"
)


def seed_database():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)
    products_df = pd.read_csv(PRODUCTS_PATH)

    if df.empty:
        raise ValueError("Dataset is empty.")

    # ---------------------------------------------------------
    # Prepare data
    # ---------------------------------------------------------

    df["sale_date"] = pd.to_datetime(
        df["sale_date"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "product_id",
            "sale_date",
            "quantity_sold",
            "selling_price",
        ]
    )

    print(f"Valid rows: {len(df)}")

    db = SessionLocal()

    try:

        # =====================================================
        # 1. PRODUCTS
        # =====================================================

        print("Seeding products...")

        unique_products = df.drop_duplicates(
            subset=["product_id"]
        )

        product_catalog = products_df.set_index(
            "product_id"
        )

        products_added = 0

        for _, row in unique_products.iterrows():

            product_id = str(row["product_id"])

            existing_product = db.scalar(
                select(Product).where(
                    Product.product_id == product_id
                )
            )

            catalog_product = None

            if product_id in product_catalog.index:
                catalog_product = product_catalog.loc[
                    product_id
                ]

            if catalog_product is not None:
                product_name = str(
                    catalog_product["product_name"]
                )
                category = str(
                    catalog_product["category"]
                )
                current_price = float(
                    catalog_product["base_price"]
                )
            else:
                product_name = f"Product {product_id}"
                category = None
                current_price = float(row["base_price"])

            if existing_product:
                existing_product.name = product_name
                existing_product.category = category
                existing_product.current_price = current_price
                continue

            product = Product(
                product_id=product_id,
                name=product_name,
                category=category,
                current_price=current_price,
            )

            db.add(product)
            products_added += 1

        db.commit()

        print(f"Products added: {products_added}")

        # =====================================================
        # 2. SALES
        # =====================================================

        print("Seeding sales...")

        sales_added = 0

        for _, row in df.iterrows():

            product_id = str(row["product_id"])
            sale_date = row["sale_date"].date()
            quantity = float(row["quantity_sold"])
            sale_price = float(row["selling_price"])

            # Prevent duplicate sales
            existing_sale = db.scalar(
                select(Sale).where(
                    Sale.product_id == product_id,
                    Sale.sale_date == sale_date,
                    Sale.quantity == quantity,
                    Sale.sale_price == sale_price,
                )
            )

            if existing_sale:
                continue

            sale = Sale(
                product_id=product_id,
                sale_date=sale_date,
                quantity=quantity,
                sale_price=sale_price,
            )

            db.add(sale)
            sales_added += 1

        db.commit()

        print(f"Sales added: {sales_added}")

        print("\nDatabase seeding completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()