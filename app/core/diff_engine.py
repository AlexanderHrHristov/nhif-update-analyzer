
from dataclasses import dataclass, fields

from app.database.models import NDUProduct


@dataclass
class FieldChange:
    field_name: str
    old_value: object
    new_value: object


@dataclass
class ProductChange:
    old: NDUProduct
    new: NDUProduct
    changes: list[FieldChange]


@dataclass
class DiffResult:
    new_products: list[NDUProduct]
    removed_products: list[NDUProduct]
    pending_removal: list[NDUProduct]
    newly_flagged: list[NDUProduct]
    financial_changes: list[ProductChange]
    other_changes: list[ProductChange]


class DiffEngine:

    FINANCIAL_FIELDS = {
        "reimbursement_value",
        "package_price",
        "patient_difference",
    }

    def compare(
        self,
        old_products: list[NDUProduct],
        new_products: list[NDUProduct],
    ) -> DiffResult:

        # Речник: НЗОК код -> продукт
        old_by_code = {
            p.nhif_code: p for p in old_products
        }
        new_by_code = {
            p.nhif_code: p for p in new_products
        }

        old_codes = set(old_by_code)
        new_codes = set(new_by_code)

        # Разлика между множествата
        added_codes = new_codes - old_codes
        removed_codes = old_codes - new_codes
        common_codes = old_codes & new_codes

        new_items = [
            new_by_code[code]
            for code in sorted(added_codes)
        ]

        removed_items = [
            old_by_code[code]
            for code in sorted(removed_codes)
        ]

        pending = sorted(
            (
                p for p in new_products
                if p.is_pending_removal
            ),
            key=lambda p: p.nhif_code,
        )

        newly_flagged = []
        financial_changes = []
        other_changes = []

        for code in sorted(common_codes):
            old = old_by_code[code]
            new = new_by_code[code]

            if (
                old.status_flag != "1"
                and new.status_flag == "1"
            ):
                newly_flagged.append(new)

            changed_fields = []

            for field in fields(NDUProduct):
                name = field.name

                old_value = getattr(old, name)
                new_value = getattr(new, name)

                if old_value != new_value:
                    changed_fields.append(
                        FieldChange(
                            field_name=name,
                            old_value=old_value,
                            new_value=new_value,
                        )
                    )

            if not changed_fields:
                continue

            financial = [
                change for change in changed_fields
                if change.field_name in self.FINANCIAL_FIELDS
            ]

            other = [
                change for change in changed_fields
                if change.field_name not in self.FINANCIAL_FIELDS
            ]

            if financial:
                financial_changes.append(
                    ProductChange(old, new, financial)
                )

            if other:
                other_changes.append(
                    ProductChange(old, new, other)
                )

        return DiffResult(
            new_products=new_items,
            removed_products=removed_items,
            pending_removal=pending,
            newly_flagged=newly_flagged,
            financial_changes=financial_changes,
            other_changes=other_changes,
        )
