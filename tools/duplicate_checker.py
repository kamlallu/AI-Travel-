import json
import os
from langchain.tools import tool

CLAIM_FILE = os.path.join("data", "claims.json")


@tool
def check_duplicate(employee_id: str, category: str, amount: float) -> dict:
    """
    Checks whether the reimbursement claim already exists.
    Returns a structured response.
    """

    if not os.path.exists(CLAIM_FILE):
        return {
            "status": "PASS",
            "duplicate_found": False,
            "message": "No previous claims found."
        }

    with open(CLAIM_FILE, "r", encoding="utf-8") as f:
        claims = json.load(f)

    for claim in claims:
        if (
            claim["employee_id"] == employee_id
            and claim["category"] == category
            and claim["amount"] == amount
        ):
            return {
                "status": "REJECT",
                "duplicate_found": True,
                "message": (
                    f"Duplicate claim detected for employee {employee_id}."
                )
            }

    return {
        "status": "PASS",
        "duplicate_found": False,
        "message": "No duplicate claim found."
    }