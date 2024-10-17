from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


app = FastAPI()

# html 문서를 위한 객체
templates = Jinja2Templates(directory="templates")

# 홈 : localhost:8000/
@app.get("/")
async def home(request: Request):
    data = "hello my project"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "data": data}
        )
# 대시보드처리 : localhost:8000/dashboard
@app.get("/dashboard")
async def dashboard(request: Request):
    data = "hello my project"
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "data": data}
        )