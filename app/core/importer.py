
import hashlib
from datetime import date
from pathlib import Path

from app.core.ndu_parser import NDUParser
from app.database.repository import ProductRepository


class NDUImporter:

    def __init__(self):
        self.parser = NDUParser()
        self.repository = ProductRepository()

    @staticmethod
    def calculate_checksum(file_path: Path) -> str:
        """Изчислява SHA-256 на съдържанието."""

        hasher = hashlib.sha256()

        with file_path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(65536), b""
            ):
                hasher.update(chunk)

        return hasher.hexdigest()

    def import_file(
        self,
        file_path: str | Path,
        effective_date: date,
    ) -> tuple[int, int]:

        file_path = Path(file_path)

        checksum = self.calculate_checksum(file_path)

        products = self.parser.parse_file(file_path)

        batch_id = self.repository.import_snapshot(
            effective_date=effective_date,
            file_path=file_path,
            checksum=checksum,
            products=products,
        )

        return batch_id, len(products)
