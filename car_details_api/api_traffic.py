import json
from typing import Dict, Any, Optional
import httpx

from hebrew_english_mapping import record_by_language

CKAN_BASE = "https://data.gov.il/api/3/action"
MOT_VEHICLES_RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"
LANGUAGE = "en" # he

async def fetch_vehicle_by_plate(
    plate: str,
    timeout: float = 20.0,
) -> Optional[Dict[str, Any]]:
    """
    Fetch a vehicle record from Israel MoT open data by EXACT license plate match.

    - No fuzzy matching
    - No prefix matching
    - Safe for 7- and 8-digit plates
    - Returns None if not found
    """

    # Normalize: digits only (no spaces / hyphens)
    plate_digits = "".join(ch for ch in plate if ch.isdigit())
    if not plate_digits:
        return None

    url = f"{CKAN_BASE}/datastore_search"
    params = {
        "resource_id": MOT_VEHICLES_RESOURCE_ID,
        "filters": json.dumps({"mispar_rechev": plate_digits}),
        "limit": 1,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    if not payload.get("success"):
        return None

    records = payload.get("result", {}).get("records", [])
    return records[0] if records else None


import asyncio
async def main():
    record = await fetch_vehicle_by_plate("28479503")

    if record:
        record_view = record_by_language(record, LANGUAGE)
        print(json.dumps(record_view, ensure_ascii=False, indent=2))
    else:
        print("Vehicle not found")


if __name__ == "__main__":
    asyncio.run(main())
