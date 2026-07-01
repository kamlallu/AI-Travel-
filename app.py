from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from models.schemas import Claim
from agent.agent import evaluate_claim

app = FastAPI(
    title="AI Travel Reimbursement Approval Agent",
    version="1.0.0",
    description="AI-powered Travel Reimbursement Approval System"
)

# Mount Static Folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates Folder
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/evaluate-claim")
async def evaluate(claim: Claim):

    try:
        result = evaluate_claim(claim.model_dump())

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Agent execution failed.",
                "details": str(e)
            }
        )

    if not result:
        return JSONResponse(
            status_code=500,
            content={
                "error": "No response received from Gemini."
            }
        )

    if isinstance(result, dict):
        return JSONResponse(content=result)

    result = str(result).strip()

    if result.startswith("```json"):
        result = result.replace("```json", "").replace("```", "").strip()

    elif result.startswith("```"):
        result = result.replace("```", "").strip()

    try:
        parsed_json = json.loads(result)

        return JSONResponse(content=parsed_json)

    except json.JSONDecodeError:

        return JSONResponse(
            status_code=500,
            content={
                "error": "Gemini did not return valid JSON.",
                "raw_response": result
            }
        )