from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models

app = FastAPI()


# models에 정의한 모든 클래스, 연결한 DB엔진에 테이블로 생성
models.Base.metadata.create_all(bind=engine)

# DB 테이블 CRUD 의존성 주입을 위한 함수 정의
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
async def dashboard(request: Request, db: Session = Depends(get_db)):
    data = "hello my project"
    # DB 테이블 조회, 월 기준으로 오름차순 정렬
    sales_datas = db.query(models.Sales).order_by(models.Sales.month.asc())
    print(sales_datas)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "data": data, "sales_datas": sales_datas}
        )

## 월 중복시 업데이트 되도록
@app.post("/dashboard")
async def create_or_update_sales(request: Request, db: Session = Depends(get_db), 
                                 month: str = Form(...), sales_amount: float = Form(...)):

    # 동일한 month 값이 있는지 확인
    existing_sale = db.query(models.Sales).filter(models.Sales.month == month).first()

    if existing_sale:
        # 중복된 데이터가 있을 경우 업데이트
        existing_sale.sales_amount = sales_amount
        db.commit()
        # db.refresh(existing_sale)
        message = f"{month}의 매출 데이터가 업데이트되었습니다."
        print(message)
    else:
        # 새로운 매출 데이터 저장
        new_sale = models.Sales(sales_amount=sales_amount, month=month)
        db.add(new_sale)
        db.commit()
        message = f"{month}의 매출 데이터가 새로 추가되었습니다."
        print(message)
        # 저장 후 다시 동일한 URL로 리디렉션 (데이터를 새로고침)
    # 방법1 url="/dashboard" <- 엔드포인트 path를 의미함
    # return RedirectResponse(url="/dashboard",  status_code=303)

    # 방법2 url=app.url_path_for("dashboard") <- 엔드포인트 함수 호출을 의미함
    return RedirectResponse(url=app.url_path_for("dashboard"), status_code=303)


# /face_recog
@app.get("/face_recog")
async def face_recog(request: Request):
    # 비즈니스 로직 넣기
    print("얼굴인식 로직")
    return templates.TemplateResponse(
    "face_recog.html",
    {"request": request}
    )