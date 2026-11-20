
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.database.models import NDUProduct


@dataclass(frozen=True)
class ProductChangeRow:
    national_number: str
    nhif_code: str
    product_name: str
    manufacturer: str
    change_type: str
    reimbursement_percent: Optional[Decimal]
    old_reimbursement: Optional[Decimal]
    new_reimbursement: Optional[Decimal]
    old_price: Optional[Decimal]
    new_price: Optional[Decimal]
    changed_fields: str


def build_change_row(
    old: NDUProduct | None,
    new: NDUProduct | None,
    change_type: str,
    changed_fields: str = "",
) -> ProductChangeRow:
    """Преобразува стара и нова версия в ред за таблицата."""

    if old is None and new is None:
        raise ValueError(
            "Необходимо е поне едно състояние на продукта."
        )

    # За нови и променени продукти използваме новите данни.
    # За отпаднали продукти използваме старите данни.
    product = new if new is not None else old

    # Изчисляваме процента на реимбурсация.
    reimbursement_percent = None

    if (
        new is not None
        and new.package_price is not None
        and new.package_price > 0
        and new.reimbursement_value is not None
    ):
        reimbursement_percent = (
            new.reimbursement_value
            / new.package_price
            * Decimal("100")
        ).quantize(Decimal("0.01"))

    # Създаваме пълното описание на продукта:
    # Име | Брой в опаковка | Лекарствена форма
    name_parts = [
        product.name,
        product.package_text,
        product.pharmaceutical_form,
    ]

    product_name = " | ".join(
        str(value).strip()
        for value in name_parts
        if value is not None and str(value).strip()
    )

    # Връщаме готовия ред за таблицата и Excel.
    return ProductChangeRow(
        national_number=product.national_number,
        nhif_code=product.nhif_code,
        product_name=product_name,
        manufacturer=product.manufacturer,
        change_type=change_type,
        reimbursement_percent=reimbursement_percent,
        old_reimbursement=(
            old.reimbursement_value if old else None
        ),
        new_reimbursement=(
            new.reimbursement_value if new else None
        ),
        old_price=(
            old.package_price if old else None
        ),
        new_price=(
            new.package_price if new else None
        ),
        changed_fields=changed_fields,
    )
