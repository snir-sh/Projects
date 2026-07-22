import asyncio
import httpx
import json
from typing import Optional
from typing import List, Dict, Any

API_BASE = "https://data.gov.il/api/3/action"

async def find_resource_id_by_dataset_title(
    title_contains: str,
    timeout: float = 20.0,
) -> Optional[str]:

    url = f"{API_BASE}/package_search"
    params = {"q": title_contains, "rows": 5}

    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    results = data.get("result", {}).get("results", [])
    for dataset in results:
        for res in dataset.get("resources", []):
            if res.get("datastore_active"):
                return res.get("id")

    return None


async def fetch_ownership_history_dynamic(
    plate: str,
) -> List[Dict[str, Any]]:
    plate_digits = "".join(ch for ch in plate if ch.isdigit())
    if not plate_digits:
        return []

    resource_id = await find_resource_id_by_dataset_title("היסטוריית כלי רכב")
    if not resource_id:
        return []

    url = f"{API_BASE}/datastore_search"
    params = {
        "resource_id": resource_id,
        "filters": json.dumps({"mispar_rechev": plate_digits}),
        "limit": 100,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    return data.get("result", {}).get("records", [])


def compute_hand_number(records: list[dict]) -> int:
    if not records:
        return 1
    return len(records)


# Data exist only for years 2017 and forward
async def main():
    records = await fetch_ownership_history_dynamic("1111111")
    hand = compute_hand_number(records)
    print("Ownership records:", len(records))
    print("Hand number:", hand)

asyncio.run(main())
