
from pathlib import Path

from app.core.ndu_parser import NDUParser
from app.core.diff_engine import DiffEngine


def main():
    parser = NDUParser()
    engine = DiffEngine()

    old_file = Path("updates/DrugsNew-01-08-2026.NDU")
    new_file = Path("updates/DrugsNew-16-08-2026.NDU")

    old_products = parser.parse_file(old_file)
    new_products = parser.parse_file(new_file)

    result = engine.compare(old_products, new_products)

    print("\n=== NHIF UPDATE COMPARISON ===")
    print(f"Стари продукти: {len(old_products)}")
    print(f"Нови продукти: {len(new_products)}")

    print(f"\nДобавени: {len(result.new_products)}")
    for p in result.new_products:
        print(f"  + {p.nhif_code} | {p.name}")

    print(f"\nОтпаднали: {len(result.removed_products)}")
    for p in result.removed_products:
        print(f"  - {p.nhif_code} | {p.name}")

    print(f"\nПредстоящо отпадане: {len(result.pending_removal)}")
    for p in result.pending_removal:
        print(f"  ! {p.nhif_code} | {p.name}")

    print(f"\nНов флаг за отпадане: {len(result.newly_flagged)}")

    print(
        f"\nФинансови промени: "
        f"{len(result.financial_changes)}"
    )

    for product_change in result.financial_changes[:10]:
        print(
            f"\n{product_change.new.nhif_code} | "
            f"{product_change.new.name}"
        )

        for change in product_change.changes:
            print(
                f"  {change.field_name}: "
                f"{change.old_value} -> {change.new_value}"
            )

    print(
        f"\nДруги промени: "
        f"{len(result.other_changes)}"
    )


if __name__ == "__main__":
    main()
