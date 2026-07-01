import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from agent.prompt import SYSTEM_PROMPT

from tools.policy_lookup import lookup_policy
from tools.receipt_checker import check_receipt
from tools.limit_checker import check_limit
from tools.duplicate_checker import check_duplicate
from tools.approval_checker import check_approval

# ----------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# ----------------------------------------------------
# Initialize Gemini
# ----------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=google_api_key,
    temperature=0,
)

# ----------------------------------------------------
# Evaluate Claim
# ----------------------------------------------------

def evaluate_claim(claim: dict):

    audit_trail = []

    try:

        # ------------------------------------------------
        # Policy Lookup
        # ------------------------------------------------

        policy = lookup_policy.invoke(
            {
                "category": claim["category"]
            }
        )

        audit_trail.append(
            {
                "tool": "Policy Lookup",
                "status": policy["status"],
                "result": policy["message"]
            }
        )

        # ------------------------------------------------
        # Receipt Check
        # ------------------------------------------------

        receipt = check_receipt.invoke(
            {
                "category": claim["category"],
                "amount": claim["amount"],
                "receipt": claim["receipt"]
            }
        )

        audit_trail.append(
            {
                "tool": "Receipt Checker",
                "status": receipt["status"],
                "result": receipt["message"]
            }
        )

        # ------------------------------------------------
        # Limit Check
        # ------------------------------------------------

        limit = check_limit.invoke(
            {
                "category": claim["category"],
                "amount": claim["amount"]
            }
        )

        audit_trail.append(
            {
                "tool": "Limit Checker",
                "status": limit["status"],
                "result": limit["message"]
            }
        )

        # ------------------------------------------------
        # Duplicate Check
        # ------------------------------------------------

        duplicate = check_duplicate.invoke(
            {
                "employee_id": claim["employee_id"],
                "category": claim["category"],
                "amount": claim["amount"]
            }
        )

        audit_trail.append(
            {
                "tool": "Duplicate Checker",
                "status": duplicate["status"],
                "result": duplicate["message"]
            }
        )

        # ------------------------------------------------
        # Manager Approval Check
        # ------------------------------------------------

        approval = check_approval.invoke(
            {
                "amount": claim["amount"],
                "manager_approval": claim["manager_approval"]
            }
        )

        audit_trail.append(
            {
                "tool": "Approval Checker",
                "status": approval["status"],
                "result": approval["message"]
            }
        )

        # ------------------------------------------------
        # Gemini Prompt
        # ------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

You are an AI Travel Reimbursement Approval Agent.

A reimbursement claim has already been validated using company business-rule tools.

Use ONLY the outputs from the tools to make the final decision.

==========================
CLAIM
==========================

Employee ID : {claim["employee_id"]}

Category : {claim["category"]}

Amount : ₹{claim["amount"]}

Receipt Submitted : {claim["receipt"]}

Manager Approval : {claim["manager_approval"]}

==========================
TOOL OUTPUTS
==========================

Policy Lookup

Status : {policy["status"]}

Reference : {policy.get("policy_reference","")}

Policy :

{policy.get("policy_text","")}

Message :

{policy["message"]}

--------------------------------

Receipt Check

Status : {receipt["status"]}

Message :

{receipt["message"]}

--------------------------------

Limit Check

Status : {limit["status"]}

Approved Amount :

{limit["approved_amount"]}

Deduction :

{limit["deduction"]}

Message :

{limit["message"]}

--------------------------------

Duplicate Check

Status : {duplicate["status"]}

Message :

{duplicate["message"]}

--------------------------------

Approval Check

Status : {approval["status"]}

Message :

{approval["message"]}

==========================

Decision Rules

1. Duplicate Claim → Reject

2. Missing Mandatory Receipt → Manual Review

3. Unknown Category → Manual Review

4. Manager Approval Missing → Manual Review

5. Exceeds Policy Limit → Partially Approve

6. Otherwise → Approve

==========================

Return ONLY valid JSON.

No markdown.

No explanation.

No ```json.

Return this format exactly:

{{
    "decision": "",
    "approved_amount": 0,
    "deduction": 0,
    "missing_documents": [],
    "policy_reference": "",
    "confidence": 0.0,
    "reason": ""
}}
"""
                # ------------------------------------------------
        # Invoke Gemini
        # ------------------------------------------------

        response = llm.invoke(prompt)

        result = response.content.strip()

        # ------------------------------------------------
        # Remove Markdown if Present
        # ------------------------------------------------

        if result.startswith("```json"):

            result = result.replace("```json", "").replace("```", "").strip()

        elif result.startswith("```"):

            result = result.replace("```", "").strip()

        # ------------------------------------------------
        # Parse JSON
        # ------------------------------------------------

        parsed_result = json.loads(result)

        # ------------------------------------------------
        # Ensure Required Fields Exist
        # ------------------------------------------------

        parsed_result.setdefault("decision", "Manual Review")
        parsed_result.setdefault("approved_amount", 0)
        parsed_result.setdefault("deduction", 0)
        parsed_result.setdefault("missing_documents", [])
        parsed_result.setdefault("policy_reference", "")
        parsed_result.setdefault("confidence", 0.0)
        parsed_result.setdefault("reason", "")

        # ------------------------------------------------
        # Business Rule Validation
        # ------------------------------------------------

        parsed_result["rule_validation"] = {

            "policy": policy["status"],

            "receipt": receipt["status"],

            "limit": limit["status"],

            "duplicate": duplicate["status"],

            "approval": approval["status"]

        }

        # ------------------------------------------------
        # Audit Trail
        # ------------------------------------------------

        parsed_result["audit_trail"] = audit_trail

        return parsed_result

    except Exception as e:

        return {

            "decision": "Manual Review",

            "approved_amount": 0,

            "deduction": 0,

            "missing_documents": [],

            "policy_reference": "",

            "confidence": 0.0,

            "reason": f"System Error: {str(e)}",

            "rule_validation": {

                "policy": "Error",

                "receipt": "Error",

                "limit": "Error",

                "duplicate": "Error",

                "approval": "Error"

            },

            "audit_trail": audit_trail

        }