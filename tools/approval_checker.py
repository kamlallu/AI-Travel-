from langchain.tools import tool

APPROVAL_LIMIT = 20000


@tool
def check_approval(amount: float, manager_approval: bool) -> dict:
    """
    Checks whether manager approval is required based on the claim amount.
    Returns a structured response.
    """

    if amount > APPROVAL_LIMIT and not manager_approval:
        return {
            "status": "MANUAL_REVIEW",
            "approval_required": True,
            "manager_approval": manager_approval,
            "threshold": APPROVAL_LIMIT,
            "message": (
                f"Claim amount ₹{amount} exceeds ₹{APPROVAL_LIMIT}. "
                "Manager approval is required."
            )
        }

    return {
        "status": "PASS",
        "approval_required": amount > APPROVAL_LIMIT,
        "manager_approval": manager_approval,
        "threshold": APPROVAL_LIMIT,
        "message": "Approval requirement satisfied."
    }