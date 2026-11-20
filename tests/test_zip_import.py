
import zipfile
import sys
from datetime import date
from pathlib import Path

from app.core.zip_importer import ZIPImporter


def main():
    if len(sys.argv) != 2:
        print(
            "Употреба: python -m tests.test_zip_import "
            '"updates/име-на-архив.zip"'
        )
        return

    zip_path = Path(sys.argv[1])

    importer = ZIPImporter()

    try:
        batch_id, count = importer.import_zip(
            zip_path=zip_path,
            effective_date=date(2026, 7, 16),
        )

        print(f"Импортиран ZIP: {zip_path.name}")
        print(f"Batch ID: {batch_id}")
        print(f"Продукти: {count}")

    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as exc:
        print(f"Грешка: {exc}")


if __name__ == "__main__":
    main()
