
from datetime import date
from pathlib import Path

from app.core.importer import NDUImporter
from app.core.diff_engine import DiffEngine
from app.database.repository import ProductRepository


def main():
    repository = ProductRepository()
    importer = NDUImporter()
    engine = DiffEngine()

    old_date = date(2026, 8, 1)
    new_date = date(2026, 8, 16)

    old_batch = repository.get_batch_by_date(old_date)

    if old_batch is None:
        batch_id, count = importer.import_file(
            file_path=Path(
                "updates/DrugsNew-01-08-2026.NDU"
            ),
            effective_date=old_date,
        )

        print(f"Импортирана историческа актуализация: {count}")
        old_batch = repository.get_batch_by_date(old_date)
    else:
        print("Актуализацията от 01.08 вече е в базата.")

    new_batch = repository.get_batch_by_date(new_date)

    if new_batch is None:
        raise ValueError(
            "Липсва актуализацията от 16.08.2026."
        )

    old_products = repository.get_products(old_batch["id"])
    new_products = repository.get_products(new_batch["id"])

    result = engine.compare(old_products, new_products)

    print("\n=== DATABASE COMPARISON ===")
    print(f"01.08: {len(old_products)} продукта")
    print(f"16.08: {len(new_products)} продукта")

    print(f"Нови: {len(result.new_products)}")
    print(f"Отпаднали: {len(result.removed_products)}")
    print(f"Финансови промени: {len(result.financial_changes)}")
    print(f"Други промени: {len(result.other_changes)}")
    print(f"С преходен флаг: {len(result.pending_removal)}")


if __name__ == "__main__":
    main()
