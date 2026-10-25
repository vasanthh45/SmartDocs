from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse




from fastapi import FastAPI, Query
from search_engine import search_banking_faqs

app = FastAPI(
    title="SmartDocs API",
    description="Search a banking FAQ knowledge base",
    version="1.0.0"
)
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


@app.get("/",
         include_in_schema=False)
def serve_homepage():
    return FileResponse(BASE_DIR / "static" / "index.html")




@app.get("/search")
def search(
    question: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=20)
):
    results = search_banking_faqs(
        question,
        number_of_results=limit
    )

    return {
        "question": question,
        "total_results": len(results),
        "results": results.to_dict(orient="records")
    }