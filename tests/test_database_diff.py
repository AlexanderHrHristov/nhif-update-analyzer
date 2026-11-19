
from datetime import date
from pathlib import Path

from app.core.ndu_parser import NDUParser
from app.core.diff_engine import DiffEngine
from app.database.repository import ProductRepository


def main():
    repository = ProductRepository()
    parser = NDUParser()
    engine = DiffEngine()

    batch = repository.get_batch_by_date(
        date(2026, 8, 16)
    )

    if batch is None:
        print("Актуализацията не е намерена в базата.")
        return

    database_products = repository.get_products(batch["id"])

    file_products = parser.parse_file(
        Path("updates/DrugsNew-16-08-2026.NDU")
    )

    result = engine.compare(
        database_products,
        file_products,
    )

    print(f"Продукти от SQLite: {len(database_products)}")
    print(f"Продукти от NDU: {len(file_products)}")

    print(f"Нови: {len(result.new_products)}")
    print(f"Отпаднали: {len(result.removed_products)}")
    print(f"Финансови промени: {len(result.financial_changes)}")
    print(f"Други промени: {len(result.other_changes)}")
    print(f"С флаг за отпадане: {len(result.pending_removal)}")


if __name__ == "__main__":
    main()
