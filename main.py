from fastapi import FastAPI, Form, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from face_recog import FaceRecog, video_process
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


# static 폴더(정적파일 폴더)를 app에 연결
app.mount("/static", StaticFiles(directory="static"), name="static")

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

## 비디오 피드 엔드포인트
@app.get("/face_recog")
def face_recog():
    # FaceRecog 인스턴스 생성
    print("얼굴인식 스트리밍")
    face_recog_instance = FaceRecog()    
    # 스트리밍 응답
    return StreamingResponse(video_process(face_recog_instance), media_type="multipart/x-mixed-replace; boundary=frame")

# HTML 페이지 렌더링 엔드포인트
@app.get("/face_recog_view")
def get_video_page(request: Request):
    print("얼굴인식 html 렌더링 페이지 ")
    return templates.TemplateResponse("face_recog.html", {"request": request})


# todo 앱 엔드포인들
# localhost:8000/
@app.get("/todo_list")
async def todo_list(request: Request, db_ss: Session = Depends(get_db)):
    # db 객체 생성, 세션연결하기 <- 의존성 주임으로 처리
    # 테이블 조회
    todos = db_ss.query(models.Todo) \
        .order_by(models.Todo.id.desc())
    print(type(todos))
    # db 조회한 결과를 출력함
    # for todo in todos:
    #     print(todo.id, todo.task, todo.completed)

    return templates.TemplateResponse(
        "todos/todo_list.html",
        {"request": request, "todos": todos}
        )

@app.post("/add")
async def add(request: Request, task: str = Form(...), 
              db_ss: Session = Depends(get_db)):
    # 클라이언트에서 textarea에서 입력 데이터 넘어온것 확인
    print(task)
    # 클라이언트에서 넘어온 task를 Todo 객체로 생성
    todo = models.Todo(task=task)
    # 의존성 주입에서 처리함 Depends(get_db) : 엔진객체생성, 세션연결
    # db 테이블에 task 저장하기
    print(todo)
    db_ss.add(todo)
    # db에 실제 저장, commit
    db_ss.commit()
    # home 엔드포인함수로 제어권을 넘김
    return RedirectResponse(url=app.url_path_for("todo_list"), 
                            status_code=status.HTTP_303_SEE_OTHER)

# 문제 : todo 1개 삭제
@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db_ss: Session = Depends(get_db)):
    todo = db_ss.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db_ss.delete(todo)
    db_ss.commit()
    return RedirectResponse(url=app.url_path_for("todo_list"), status_code=status.HTTP_303_SEE_OTHER)

# todo 수정을 위한 조회
@app.get("/edit/{todo_id}")
async def edit(request: Request, todo_id: int , db_ss: Session = Depends(get_db)):
    # 요청 수정 처리
    todo = db_ss.query(models.Todo).filter(models.Todo.id==todo_id).first()
    print(todo.task)

    return templates.TemplateResponse(
        "todos/edit.html",
        {"request": request, "todo": todo}
        )
# todo 업데이터 처리
@app.post("/edit/{todo_id}")
async def add(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(False), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(url=app.url_path_for("todo_list"), status_code=status.HTTP_303_SEE_OTHER)


