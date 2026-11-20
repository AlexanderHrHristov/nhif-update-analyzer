
from datetime import date

from app.core.change_row import build_change_row
from app.database.repository import ProductRepository


def main():
    repository = ProductRepository()

    batch = repository.get_batch_by_date(
        date(2026, 8, 16)
    )

    if batch is None:
        print("Актуализацията не е намерена.")
        return

    products = repository.get_products(batch["id"])

    if not products:
        print("Няма продукти.")
        return

    product = products[0]

    row = build_change_row(
        old=None,
        new=product,
        change_type="Нов",
        changed_fields="Нов продукт",
    )

    print("National number:", row.national_number)
    print("НЗОК код:", row.nhif_code)
    print("Продукт:", row.product_name)
    print("Производител:", row.manufacturer)
    print("Вид промяна:", row.change_type)
    print("Реимбурсация %:", row.reimbursement_percent)
    print("Стара реимбурсация:", row.old_reimbursement)
    print("Нова реимбурсация:", row.new_reimbursement)
    print("Стара цена:", row.old_price)
    print("Нова цена:", row.new_price)
    print("Променени полета:", row.changed_fields)


if __name__ == "__main__":
    main()
