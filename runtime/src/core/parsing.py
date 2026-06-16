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
    "setenta": Decimal("70"),
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

FRACTION_WORDS: dict[str, Decimal] = {
    "mitad": Decimal("0.5"),
    "medio": Decimal("0.5"),
    "media": Decimal("0.5"),
    "un cuarto": Decimal("0.25"),
    "cuarto": Decimal("0.25"),
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


def parse_stock_observations(text: str) -> list[dict[str, Any]]:
    normalized_text = normalize(text)
    clauses = [clause.strip() for clause in re.split(r"[,.;?]", normalized_text) if clause.strip()]
    observations: list[dict[str, Any]] = []
    pattern = re.compile(
        r"(?P<qty>\d+(?:[.,]\d+)?|un|una|uno)\s+bolsa"
        r"(?:\s+y\s+(?P<fraction>un cuarto|cuarto|medio|media|mitad))?"
        r"\s+de\s+(?P<tail>.+)"
    )
    for clause in clauses:
        match = pattern.search(clause)
        if not match:
            apply_percentage_to_previous_observation(clause, observations)
            continue
        quantity = parse_decimal(match.group("qty"))
        if quantity is None:
            continue
        fraction = parse_fraction(match.group("fraction"))
        tail = match.group("tail")
        product = clean_inventory_product(tail)
        if not product:
            continue
        percentage = parse_percentage(tail)
        if percentage is None:
            percentage = parse_remaining_fraction(tail)
        package_kg = parse_package_kg(tail)
        if fraction is not None:
            estimated_bags = quantity + fraction
        elif percentage is not None:
            estimated_bags = quantity * percentage
        else:
            estimated_bags = quantity
        observation: dict[str, Any] = {
            "estado": "pending_review",
            "producto": product,
            "unidad": "bolsa",
            "cantidad_reportada": number_to_json(quantity),
            "bolsas_estimadas_restantes": number_to_json(estimated_bags),
            "fuente": "conversacion",
        }
        if percentage is not None:
            observation["porcentaje_restante_inferido"] = number_to_json(percentage * Decimal("100"))
        if package_kg is not None:
            observation["peso_bolsa_kg"] = number_to_json(package_kg)
            observation["kg_estimados_restantes"] = number_to_json(estimated_bags * package_kg)
        observations.append(observation)
    return observations


def apply_percentage_to_previous_observation(
    clause: str,
    observations: list[dict[str, Any]],
) -> None:
    if not observations:
        return
    percentage = parse_percentage(clause)
    if percentage is None:
        return
    previous = observations[-1]
    if "porcentaje_restante_inferido" in previous:
        return
    quantity = Decimal(str(previous["cantidad_reportada"]))
    estimated_bags = quantity * percentage
    previous["porcentaje_restante_inferido"] = number_to_json(percentage * Decimal("100"))
    previous["bolsas_estimadas_restantes"] = number_to_json(estimated_bags)
    if "peso_bolsa_kg" in previous:
        package_kg = Decimal(str(previous["peso_bolsa_kg"]))
        previous["kg_estimados_restantes"] = number_to_json(estimated_bags * package_kg)


def clean_product(product: str) -> str:
    product = re.sub(r"\b(cada|una|uno|unidad|bolsa)\b.*$", "", product).strip()
    product = re.sub(r"\s+", " ", product)
    return product.strip(" .,:;")


def clean_inventory_product(value: str) -> str:
    value = re.split(
        r"\b(abierto|mas o menos|tambien|también|al\s+\d+|al\s+setenta|a la mitad|por ciento)\b",
        value,
        maxsplit=1,
    )[0]
    value = re.sub(r"\s+de\s+\d+(?:[.,]\d+)?\s+kilogramos?.*$", "", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .,:;")


def parse_fraction(value: str | None) -> Decimal | None:
    if not value:
        return None
    return FRACTION_WORDS.get(value.strip())


def parse_remaining_fraction(value: str) -> Decimal | None:
    for word, fraction in FRACTION_WORDS.items():
        if word in value:
            return fraction
    return None


def parse_percentage(value: str) -> Decimal | None:
    numeric_match = re.search(r"\b(?P<number>\d+(?:[.,]\d+)?)\s*por ciento\b", value)
    if numeric_match:
        parsed = parse_decimal(numeric_match.group("number"))
        if parsed is not None:
            return parsed / Decimal("100")
    word_match = re.search(r"\b(?P<number>setenta)\s+por ciento\b", value)
    if word_match:
        parsed = parse_decimal(word_match.group("number"))
        if parsed is not None:
            return parsed / Decimal("100")
    return None


def parse_package_kg(value: str) -> Decimal | None:
    match = re.search(r"\bde\s+(?P<kg>\d+(?:[.,]\d+)?)\s+kilogramos?\b", value)
    if not match:
        return None
    return parse_decimal(match.group("kg"))
