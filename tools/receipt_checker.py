from langchain.tools import tool


@tool
def check_receipt(category: str, amount: float, receipt: bool) -> dict:
    """
    Checks whether the required receipt is available based on company policy.
    Returns a structured response.
    """

    if category == "Hotel" and not receipt:
        return {
            "status": "MANUAL_REVIEW",
            "receipt_required": True,
            "receipt_submitted": receipt,
            "message": "Hotel receipt is missing. Manual Review is required."
        }

    if category == "Meals" and amount > 500 and not receipt:
        return {
            "status": "MANUAL_REVIEW",
            "receipt_required": True,
            "receipt_submitted": receipt,
            "message": "Meal receipt is missing for an amount above ₹500. Manual Review is required."
        }

    if category == "Flight" and not receipt:
        return {
            "status": "MANUAL_REVIEW",
            "receipt_required": True,
            "receipt_submitted": receipt,
            "message": "Flight ticket is missing. Manual Review is required."
        }

    return {
        "status": "PASS",
        "receipt_required": False,
        "receipt_submitted": receipt,
        "message": "Receipt verification passed."
    }