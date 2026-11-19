"""
from pathlib import Path

from app.core.ndu_parser import NDUParser


def main():
    file_path = Path("updates/DrugsNew-16-08-2026.NDU")

    parser = NDUParser()
    products = parser.parse_file(file_path)

    print(f"Успешно заредени продукти: {len(products)}")

    # Търсим конкретен продукт по НЗОК код.
    product = next(
        (p for p in products if p.nhif_code == "AF232"),
        None
    )

    if product:
        print("\nПримерен продукт:")
        print(f"НЗОК код: {product.nhif_code}")
        print(f"Наименование: {product.name}")
        print(f"INN: {product.inn}")
        print(f"Реимбурсация: {product.reimbursement_value}")
        print(f"Цена: {product.package_price}")
        print(f"Разлика: {product.patient_difference}")
        print(f"Предстоящо отпадане: {product.is_pending_removal}")

    pending = [
        p for p in products if p.is_pending_removal
    ]

    print(f"\nПродукти с флаг за отпадане: {len(pending)}")

    for p in pending:
        print(f"{p.nhif_code} | {p.name}")


if __name__ == "__main__":
    main()

"""


"""
from app.database.db import initialize_database


def main():
    initialize_database()


if __name__ == "__main__":
    main()
    
"""

from datetime import date
from pathlib import Path

from app.core.importer import NDUImporter
from app.database.db import initialize_database
from app.database.repository import ProductRepository


def main():
    initialize_database()

    file_path = Path(
        "updates/DrugsNew-16-08-2026.NDU"
    )

    importer = NDUImporter()

    try:
        batch_id, product_count = importer.import_file(
            file_path=file_path,
            effective_date=date(2026, 8, 16),
        )

        print(f"\nАктуализация ID: {batch_id}")
        print(f"Импортирани продукти: {product_count}")

        repository = ProductRepository()

        saved_count = repository.count_products(batch_id)

        print(f"Продукти в базата: {saved_count}")

    except ValueError as exc:
        print(f"\nИмпортът е отказан: {exc}")


if __name__ == "__main__":
    main()

