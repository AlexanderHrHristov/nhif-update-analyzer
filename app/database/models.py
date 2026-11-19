
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class NDUProduct:
    atc_code: str
    inn: str
    nhif_code: str
    name: str
    manufacturer: str
    strength: str
    package_text: str
    package_quantity: str
    pharmaceutical_form: str

    flag_10: str
    item_type: str
    field_12: str
    prescription_group: str
    flag_14: str

    reimbursement_value: Decimal
    price_source: str
    flag_17: str
    package_price: Decimal
    patient_difference: Decimal
    flag_20: str

    national_number: str
    status_flag: str

    @property
    def is_pending_removal(self) -> bool:
        return self.status_flag == "1"
