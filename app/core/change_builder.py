
from dataclasses import fields

from app.core.change_row import (
    ProductChangeRow,
    build_change_row,
)
from app.database.models import NDUProduct


FINANCIAL_FIELDS = {
    "reimbursement_value": "Реимбурсна стойност",
    "package_price": "Цена на опаковка",
    "patient_difference": "Доплащане",
}

FIELD_LABELS = {
    "name": "Наименование",
    "manufacturer": "Производител",
    "package_text": "Опаковка",
    "status_flag": "Статус",
    "national_number": "Национален номер",
}


def build_change_rows(
    old_products: list[NDUProduct],
    new_products: list[NDUProduct],
) -> list[ProductChangeRow]:
    """Създава един ред за всеки нов, отпаднал или променен продукт."""

    old_by_code = {
        product.nhif_code: product
        for product in old_products
    }

    new_by_code = {
        product.nhif_code: product
        for product in new_products
    }

    all_codes = sorted(
        set(old_by_code) | set(new_by_code)
    )

    rows = []

    for code in all_codes:
        old = old_by_code.get(code)
        new = new_by_code.get(code)

        if old is None:
            rows.append(
                build_change_row(
                    old=None,
                    new=new,
                    change_type="Нов",
                    changed_fields="Нов продукт",
                )
            )
            continue

        if new is None:
            rows.append(
                build_change_row(
                    old=old,
                    new=None,
                    change_type="Отпаднал",
                    changed_fields="Отпаднал продукт",
                )
            )
            continue

        changed = [
            field.name
            for field in fields(NDUProduct)
            if getattr(old, field.name) != getattr(new, field.name)
        ]

        if not changed:
            continue

        financial = any(
            field in FINANCIAL_FIELDS
            for field in changed
        )

        other = any(
            field not in FINANCIAL_FIELDS
            for field in changed
        )

        types = []

        if financial:
            types.append("Финансова")

        if other:
            types.append("Друга")

        labels = [
            FINANCIAL_FIELDS.get(
                field,
                FIELD_LABELS.get(field, field)
            )
            for field in changed
        ]

        rows.append(
            build_change_row(
                old=old,
                new=new,
                change_type=", ".join(types),
                changed_fields=", ".join(labels),
            )
        )

    return rows
