import os
from langchain.tools import tool

POLICY_FILE = os.path.join("data", "policy.md")


@tool
def lookup_policy(category: str) -> dict:
    """
    Retrieves the reimbursement policy for the given expense category.
    Returns a structured response.
    """

    if not os.path.exists(POLICY_FILE):
        return {
            "status": "ERROR",
            "policy_found": False,
            "policy_reference": "",
            "message": "Policy file not found."
        }

    with open(POLICY_FILE, "r", encoding="utf-8") as file:
        policy = file.read()

    lines = policy.splitlines()

    result = []
    capture = False
    policy_reference = ""

    for line in lines:

        if line.startswith("##"):

            if category.lower() in line.lower():
                capture = True
                policy_reference = line.replace("##", "").strip()
                result.append(line)
                continue

            elif capture:
                break

        elif capture:
            result.append(line)

    if result:
        return {
            "status": "PASS",
            "policy_found": True,
            "policy_reference": policy_reference,
            "policy_text": "\n".join(result),
            "message": f"Policy found for '{category}'."
        }

    return {
        "status": "MANUAL_REVIEW",
        "policy_found": False,
        "policy_reference": "",
        "policy_text": "",
        "message": (
            f"No reimbursement policy found for category '{category}'. "
            "Manual Review is required."
        )
    }