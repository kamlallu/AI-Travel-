from pydantic import BaseModel
from typing import List


class Claim(BaseModel):
    employee_id: str
    category: str
    amount: float
    receipt: bool
    manager_approval: bool


class ClaimResponse(BaseModel):
    decision: str
    approved_amount: float
    deduction: float
    missing_documents: List[str]
    policy_reference: str
    confidence: float
    reason: str