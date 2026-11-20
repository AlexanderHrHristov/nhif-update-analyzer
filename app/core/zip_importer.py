
import hashlib
import zipfile
from datetime import date
from pathlib import Path

from app.core.ndu_parser import NDUParser
from app.database.repository import ProductRepository

import re
from datetime import datetime

class ZIPImporter:

    def __init__(self):
        self.parser = NDUParser()
        self.repository = ProductRepository()

    def import_zip(
        self,
        zip_path: str | Path,
        effective_date: date,
    ) -> tuple[int, int]:

        zip_path = Path(zip_path)

        with zipfile.ZipFile(zip_path, "r") as archive:
            ndu_files = [
                name for name in archive.namelist()
                if Path(name).name.lower().startswith("drugsnew-")
                and name.lower().endswith(".ndu")
            ]

            if len(ndu_files) != 1:
                raise ValueError(
                    "ZIP архивът трябва да съдържа "
                    "точно един DrugsNew-*.NDU файл."
                )

            ndu_name = ndu_files[0]
            content = archive.read(ndu_name)

        checksum = hashlib.sha256(content).hexdigest()

        products = self.parser.parse_bytes(content)

        batch_id = self.repository.import_snapshot(
            effective_date=effective_date,
            file_path=Path(ndu_name),
            checksum=checksum,
            products=products,
        )

        return batch_id, len(products)



    def detect_effective_date(self, zip_path: str | Path) -> date:
        """Разпознава датата от името на NDU файла в ZIP."""

        with zipfile.ZipFile(zip_path, "r") as archive:
            ndu_files = [
                name for name in archive.namelist()
                if Path(name).name.lower().startswith("drugsnew-")
                and name.lower().endswith(".ndu")
            ]

            if len(ndu_files) != 1:
                raise ValueError(
                    "ZIP архивът трябва да съдържа точно един DrugsNew-*.NDU файл."
                )

            filename = Path(ndu_files[0]).name

        match = re.fullmatch(
            r"DrugsNew-(\d{2}-\d{2}-\d{4})\.ndu",
            filename,
            flags=re.IGNORECASE
        )

        if not match:
            raise ValueError(
                f"Не може да се разпознае датата от {filename}"
            )

        return datetime.strptime(
            match.group(1), "%d-%m-%Y"
        ).date()
