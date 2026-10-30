"""Validation gates for branch-specific unit prices; no inferred store or price."""
from decimal import Decimal, InvalidOperation
from typing import Any

def verify_price(*, requested_city: str, selected_store: str | None,
                 confirmed_store_city: str | None, displayed_price: Any,
                 currency: str, product_sku: str, confirmed_sku: str | None,
                 stock_status: str | None, source_url: str) -> dict:
    base = {"city": requested_city, "store": selected_store,
            "sku": product_sku, "price_clp": None, "stock": stock_status,
            "source_url": source_url, "status": "UNVERIFIED"}
    if not selected_store or not confirmed_store_city or confirmed_store_city.casefold().strip() != requested_city.casefold().strip():
        return {**base, "reason": "STORE_NOT_CONFIRMED"}
    if not confirmed_sku or confirmed_sku != product_sku:
        return {**base, "reason": "PRODUCT_NOT_CONFIRMED"}
    if currency.upper() != "CLP":
        return {**base, "reason": "CURRENCY_NOT_CONFIRMED"}
    try:
        price = Decimal(str(displayed_price))
    except (InvalidOperation, ValueError, TypeError):
        return {**base, "reason": "PRICE_NOT_CONFIRMED"}
    if not price.is_finite() or price <= 0 or price != price.to_integral_value():
        return {**base, "reason": "PRICE_NOT_CONFIRMED"}
    if stock_status not in {"available", "unavailable"}:
        return {**base, "reason": "STOCK_NOT_CONFIRMED"}
    if not source_url.startswith("https://"):
        return {**base, "reason": "SOURCE_NOT_CONFIRMED"}
    return {**base, "price_clp": int(price), "status": "VERIFIED", "reason": None}

def cheapest_available_cement(rows: list[dict]) -> dict | None:
    valid = [r for r in rows if r.get("status") == "VERIFIED"
             and r.get("stock") == "available"
             and r.get("category") == "cement_25kg"
             and r.get("brand") in {"Melón", "Polpaico"}]
    return min(valid, key=lambda r: r["price_clp"]) if valid else None
