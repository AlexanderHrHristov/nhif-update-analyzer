
from datetime import date
from collections import Counter

from app.core.change_builder import build_change_rows
from app.database.repository import ProductRepository


def main():
    repository = ProductRepository()

    old_batch = repository.get_batch_by_date(
        date(2026, 8, 1)
    )

    new_batch = repository.get_batch_by_date(
        date(2026, 8, 16)
    )

    old_products = repository.get_products(
        old_batch["id"]
    )

    new_products = repository.get_products(
        new_batch["id"]
    )

    rows = build_change_rows(
        old_products,
        new_products
    )

    counts = Counter(
        row.change_type for row in rows
    )

    print("Общо уникални променени продукти:", len(rows))

    for change_type, count in sorted(counts.items()):
        print(f"{change_type}: {count}")

    print("\nПървите 5 промени:")

    for row in rows[:5]:
        print(
            row.nhif_code,
            row.product_name,
            "|",
            row.change_type,
            "|",
            row.changed_fields,
        )


if __name__ == "__main__":
    main()
