
from datetime import date

from app.core.diff_engine import DiffEngine
from app.database.repository import ProductRepository


def compare_dates(old_date: date, new_date: date):
    repository = ProductRepository()
    engine = DiffEngine()

    old_batch = repository.get_batch_by_date(old_date)
    new_batch = repository.get_batch_by_date(new_date)

    if old_batch is None or new_batch is None:
        raise ValueError("Липсва актуализация в базата.")

    old_products = repository.get_products(old_batch["id"])
    new_products = repository.get_products(new_batch["id"])

    result = engine.compare(old_products, new_products)

    print(
        f"\n=== {old_date:%d.%m.%Y} -> "
        f"{new_date:%d.%m.%Y} ==="
    )

    print(f"Стари продукти: {len(old_products)}")
    print(f"Нови продукти: {len(new_products)}")
    print(f"Добавени: {len(result.new_products)}")
    print(f"Отпаднали: {len(result.removed_products)}")
    print(f"Финансови промени: {len(result.financial_changes)}")
    print(f"Други промени: {len(result.other_changes)}")
    print(f"С преходен флаг: {len(result.pending_removal)}")


def main():
    compare_dates(
        date(2026, 7, 16),
        date(2026, 8, 1),
    )

    compare_dates(
        date(2026, 8, 1),
        date(2026, 8, 16),
    )


if __name__ == "__main__":
    main()
