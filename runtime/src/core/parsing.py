from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from core.text import normalize


NUMBER_WORDS: dict[str, Decimal] = {
    "un": Decimal("1"),
    "una": Decimal("1"),
    "uno": Decimal("1"),
    "dos": Decimal("2"),
    "tres": Decimal("3"),
    "cuatro": Decimal("4"),
    "cinco": Decimal("5"),
    "seis": Decimal("6"),
    "siete": Decimal("7"),
    "ocho": Decimal("8"),
    "nueve": Decimal("9"),
    "diez": Decimal("10"),
}

UNIT_ALIASES: dict[str, str] = {
    "bolsa": "bolsa",
    "bolsas": "bolsa",
    "kg": "kg",
    "kilo": "kg",
    "kilos": "kg",
    "litro": "litro",
    "litros": "litro",
    "lts": "litro",
    "unidad": "unidad",
    "unidades": "unidad",
}


@dataclass(frozen=True)
class ParsedItem:
    product: str
    quantity: Decimal
    unit: str
    unit_price: Decimal | None

    @property
    def subtotal(self) -> Decimal | None:
        if self.unit_price is None:
            return None
        return self.quantity * self.unit_price

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "producto": self.product,
            "cantidad": number_to_json(self.quantity),
            "unidad": self.unit,
        }
        if self.unit_price is not None:
            data["precio_unitario"] = number_to_json(self.unit_price)
            data["subtotal_inferido"] = number_to_json(self.subtotal)
        return data


def parse_decimal(raw_value: str) -> Decimal | None:
    value = raw_value.strip().lower()
    if value in NUMBER_WORDS:
        return NUMBER_WORDS[value]
    value = value.replace("gs", "").replace("pyg", "").strip()
    value = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def number_to_json(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral():
        return int(value)
    return float(value)


def parse_items(text: str) -> list[ParsedItem]:
    normalized_text = normalize(text)
    quantity_pattern = r"(?P<qty>\d+(?:[.,]\d+)?|un|una|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)"
    unit_pattern = r"(?P<unit>bolsas?|kg|kilos?|litros?|lts|unidades?|unidad)"
    product_pattern = r"(?P<product>[a-z0-9\s]+?)"
    price_pattern = r"(?:\s+a\s+(?P<price>\d[\d.,]*)(?:\s+cada\s+(?:una|uno|bolsa|unidad))?)?"
    boundary = r"(?=\s+y\s+|\s*,|\s+\.|$)"
    pattern = re.compile(
        rf"{quantity_pattern}\s+{unit_pattern}\s+de\s+{product_pattern}{price_pattern}{boundary}"
    )

    items: list[ParsedItem] = []
    for match in pattern.finditer(normalized_text):
        quantity = parse_decimal(match.group("qty"))
        unit = UNIT_ALIASES.get(match.group("unit"), match.group("unit"))
        product = clean_product(match.group("product"))
        unit_price = parse_decimal(match.group("price")) if match.group("price") else None
        if quantity is None or not product:
            continue
        items.append(
            ParsedItem(
                product=product,
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
            )
        )
    return items


def clean_product(product: str) -> str:
    product = re.sub(r"\b(cada|una|uno|unidad|bolsa)\b.*$", "", product).strip()
    product = re.sub(r"\s+", " ", product)
    return product.strip(" .,:;")

