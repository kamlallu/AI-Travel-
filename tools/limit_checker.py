import json
import os
from langchain.tools import tool

LIMIT_FILE = os.path.join("data", "limits.json")


@tool
def check_limit(category: str, amount: float) -> dict:
    """
    Checks whether the reimbursement amount is within the allowed policy limit.
    Returns a structured response.
    """

    if not os.path.exists(LIMIT_FILE):
        return {
            "status": "ERROR",
            "limit": None,
            "approved_amount": 0,
            "deduction": 0,
            "message": "Limit configuration file not found."
        }

    with open(LIMIT_FILE, "r", encoding="utf-8") as f:
        limits = json.load(f)

    limit = limits.get(category)

    if limit is None:
        return {
            "status": "MANUAL_REVIEW",
            "limit": None,
            "approved_amount": 0,
            "deduction": 0,
            "message": (
                f"Unknown expense category '{category}'. "
                "Manual Review is required."
            )
        }

    if amount <= limit:
        return {
            "status": "PASS",
            "limit": limit,
            "approved_amount": amount,
            "deduction": 0,
            "message": (
                f"Amount ₹{amount} is within the reimbursement limit "
                f"of ₹{limit}."
            )
        }

    deduction = amount - limit

    return {
        "status": "PARTIAL_APPROVAL",
        "limit": limit,
        "approved_amount": limit,
        "deduction": deduction,
        "message": (
            f"Amount ₹{amount} exceeds the reimbursement limit of ₹{limit}. "
            f"Suggested deduction: ₹{deduction}."
        )
    }