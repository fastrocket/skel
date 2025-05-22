from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

import os
from pathlib import Path
from app.auth.router import auth_router
from app.auth.utils import get_current_user
from app.db.dynamodb import create_tables_if_not_exist

# Create FastAPI app
app = FastAPI(title="FastAPI Skeleton App")

@app.on_event("startup")
async def startup_event():
    create_tables_if_not_exist()
    print("DynamoDB tables checked/created.")

# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")

# Set up templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
    """
    Root endpoint that redirects to dashboard if logged in,
    otherwise to login page
    """
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/auth/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_current_user)):
    """
    Dashboard page, requires authentication
    """
    if not user:
        return RedirectResponse(url="/auth/login")
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "user": user}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
