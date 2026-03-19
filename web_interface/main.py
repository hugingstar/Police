from fastapi import FastAPI, Request, Form, Cookie, Depends, Query, APIRouter
from urllib.parse import quote
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from typing import Optional, List
import os
import re
import pandas as pd
import json
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from CRUD_handler import UserDBHandler
from MAIL_handler import UserMAILHandler

# FastAPI 설정
app = FastAPI(title="Kojel Private equity Fund")
api_router = APIRouter()
# 컨테이너 환경 경로 유지
templates = Jinja2Templates(directory="templates")

"""
Setting zone
"""

# domain_setting
allowed_domain = "@kojel.com"

# NFS mount directory
INBOX_BASE_PATH = "/mnt/mail_storage" 
SENT_MAIL_PATH = "/mnt/mail_storage/sent_items"

try:
    if not os.path.exists(INBOX_BASE_PATH):
        os.makedirs(INBOX_BASE_PATH, exist_ok=True) 
    if not os.path.exists(SENT_MAIL_PATH):
        os.makedirs(SENT_MAIL_PATH, exist_ok=True) 
except Exception as e:
    print(f"[WAS server] INBOX/SENTBOX folder create error: {e}")

# Mail server config
MAIL_CONFIG = {
    "MAIL_SERVER_IP" : "10.22.0.2",
    "MAIL_SEND_PORT" : 25,
    "MAIL_RECEIVE_PORT" : 110,
    "MAIL_SERVER_PORT" : 9999,
    "INBOX_BASE_PATH" : INBOX_BASE_PATH,
    "SENT_MAIL_PATH" : SENT_MAIL_PATH
}

# Database information
DB_CONFIG = {
    "host": "mariadb-service.db.svc.cluster.local", 
    "port": 3306, 
    "user": "root", 
    "password": "P@ssw0rd", 
    "db_name": "userdb", 
    "tbl_name": "members"
}

# Monitoring & Stock Config
DATA_ROOT_DIR = "/root/Data"
MARKETS = ["KOSPI", "KOSDAQ", "NASDAQ", "NYSE"]
COLUMN_MAP = {
    "time_stamp": "날짜/시간",
    "open": "시가",
    "high": "고가",
    "low": "저가",
    "close": "종가",
    "volume": "거래량",
    "close_diff_first": "전일대비",
    "RSI": "RSI",
    "Sell_Signal": "매도신호",
    "RSI_BullDiv": "상승다이버전스",
    "RSI_BearDiv": "하락다이버전스"
}

# *********************************************************************
# Extra functions
def get_current_user(user_id: Optional[str] = Cookie(None)):
    """쿠키에서 user_id를 읽어 로그인 여부 확인"""
    return user_id

# *********************************************************************
# Front-end / Auth Routes
# =====================================================================

@api_router.get("/", response_class=HTMLResponse)
async def read_form(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@api_router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@api_router.post("/login")
async def login(user_id: str = Form(...), password: str = Form(...)):
    db_handler = UserDBHandler(**DB_CONFIG)
    success, result = db_handler.verify_login(user_id, password)
    
    if success:
        message = quote(f"{result}님, 환영합니다!")
        redirect_response = RedirectResponse(url=f"/users?msg={message}", status_code=303)
        redirect_response.set_cookie(key="user_id", value=user_id, httponly=True)
        return redirect_response
    else:
        error_msg = quote(str(result))
        return RedirectResponse(url=f"/login?msg={error_msg}", status_code=303)

@api_router.get("/logout")
async def logout():
    message = quote("로그아웃 되었습니다.")
    response = RedirectResponse(url=f"/login?msg={message}", status_code=303)
    response.delete_cookie(key="user_id")
    return response

# =====================================================================
# User Management
@api_router.get("/insert", response_class=HTMLResponse)
async def insert_form(request: Request, msg: str = None):
    return templates.TemplateResponse("insert.html", {"request": request, "msg": msg})

@api_router.post("/insert")
async def create_user(
    user_id: str = Form(...), 
    password: str = Form(...),
    username: str = Form(...), 
    email: str = Form(None), 
    birthday: str = Form(None), 
    age: int = Form(0),
    department: str = Form(None), 
    emp_number: str = Form(...)
):  
    generated_email = f"{user_id}{allowed_domain}"
    if email and email != generated_email:
        message = "가입 실패: 이메일 형식이 올바르지 않습니다."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    if not re.match(r"^C\d{6}$", emp_number):
        message = "가입 실패: 인증번호는 'C'로 시작하는 7자리여야 합니다."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
    if not re.match(password_pattern, password):
        message = "가입 실패: 비밀번호 규정(대/소문자, 특수문자 포함 8자 이상)을 확인하세요."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    try:
        mail_handler = UserMAILHandler(**MAIL_CONFIG)
        mail_success = mail_handler.add_mail_user(user_id, password) 

        if mail_success:
            input_data = (user_id, password, username, generated_email, birthday, age, department, emp_number)
            db_handler = UserDBHandler(**DB_CONFIG, inputData=input_data)
            success, db_message = db_handler.execute_insert()
            message = db_message
        else:
            message = "가입 실패: 메일 서버 통신 불가"
    except Exception as e:
        message = f"가입 실패: {str(e)}"
    
    return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

# =====================================================================
# Stock Monitoring System (신규 추가 구간)
@api_router.get("/stock", response_class=HTMLResponse)
async def stock_main(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=" + quote("로그인이 필요합니다."), status_code=303)
    
    return templates.TemplateResponse("stock.html", {
        "request": request,
        "user_id": user_id,
        "email": f"{user_id}{allowed_domain}",
        "column_labels": COLUMN_MAP,
        "markets": MARKETS,
        "counts": {"bull": 0, "bear": 0, "sell": 0},
        "raw_data": json.dumps({"bull":[], "bear":[], "sell":[]}),
        "selected_date": date.today().isoformat(),
        "selected_market": "KOSPI"
    })

@api_router.post("/stock", response_class=HTMLResponse)
async def search_stock_data(
    request: Request,
    target_date: str = Form(...),
    market: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    
    folder_path = os.path.join(DATA_ROOT_DIR, market, "B1Sheet", target_date)
    data_types = {"bull": "df_bull", "bear": "df_bear", "sell": "df_sell"}
    raw_data, counts = {}, {}

    for key, filename_base in data_types.items():
        file_path = os.path.join(folder_path, f"{filename_base}.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                numeric_cols = ['open', 'close', 'volume']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                raw_data[key] = df.to_dict(orient='records')
                counts[key] = len(df)
            except:
                raw_data[key], counts[key] = [], 0
        else:
            raw_data[key], counts[key] = [], 0

    return templates.TemplateResponse("stock.html", {
        "request": request,
        "user_id": user_id,
        "email": f"{user_id}{allowed_domain}",
        "column_labels": COLUMN_MAP,
        "markets": MARKETS,
        "raw_data": json.dumps(raw_data),
        "counts": counts,
        "selected_date": target_date,
        "selected_market": market
    })

@api_router.get("/api/detail")
async def get_stock_detail(market: str, name: str):
    try:
        path = os.path.join(DATA_ROOT_DIR, market, "A1Sheet")
        target_file = next((f for f in os.listdir(path) if f.startswith(name)), None)
        if not target_file: return JSONResponse({"error": "No data found"}, status_code=404)
        
        df = pd.read_csv(os.path.join(path, target_file))
        if 'time_stamp' in df.columns:
            df['time_stamp_dt'] = pd.to_datetime(df['time_stamp'])
            max_date = df['time_stamp_dt'].max()
            start_date = max_date - pd.DateOffset(months=2)
            filtered_df = df[df['time_stamp_dt'] >= start_date].copy()
            filtered_df = filtered_df.sort_values(by='time_stamp_dt', ascending=False)
            filtered_df = filtered_df.drop(columns=['time_stamp_dt'])
            if filtered_df.columns[0].startswith('Unnamed'): filtered_df = filtered_df.iloc[:, 1:]
            return filtered_df.to_dict(orient='records')
        return df.tail(60).iloc[::-1].to_dict(orient='records')
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api_router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request, 
    msg: Optional[str] = Query(None), 
    dept: Optional[str] = Query(None), 
    name: Optional[str] = Query(None), 
    user_id: str = Depends(get_current_user)
):
    if not user_id:
        return RedirectResponse(url="/login?msg=" + quote("로그인이 필요합니다."), status_code=303)
    
    db_handler = UserDBHandler(**DB_CONFIG)
    success, result = db_handler.execute_select(dept=dept, name=name)
    table_html = result.to_html(classes='table table-striped table-hover', index=False) if success and result is not None and not result.empty else None

    return templates.TemplateResponse("users.html", {
        "request": request, 
        "table": table_html, 
        "user_id": user_id,
        "email" : f"{user_id}{allowed_domain}",
        "msg": msg or ("정보가 없습니다." if not success else None)
    })

# =====================================================================
# Mail System
@api_router.get("/mail", response_class=HTMLResponse)
async def mail_page(request: Request, msg: str = None, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    return templates.TemplateResponse("mail.html", {"request": request, "msg": msg, "user_id": user_id, "email" : f"{user_id}{allowed_domain}"})

@api_router.post("/send_mail")
async def send_mail(receiver: str = Form(...), subject: str = Form(...), content: str = Form(...), user_id: str = Depends(get_current_user)):
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    try:
        message = MIMEMultipart()
        message["From"] = generated_email
        message["To"] = receiver
        message["Subject"] = Header(subject, "utf-8").encode()
        message.attach(MIMEText(content, "plain", "utf-8"))
        with smtplib.SMTP(MAIL_CONFIG["MAIL_SERVER_IP"], MAIL_CONFIG["MAIL_SEND_PORT"]) as server:
            server.send_message(message)

        sent_file = os.path.join(SENT_MAIL_PATH, f"{user_id}")
        with open(sent_file, "a", encoding="utf-8-sig") as f:
            f.write(f"To: {receiver}\nSubject: {subject}\nDate: {pd.Timestamp.now()}\nContent: {content}\n---\n")
        return RedirectResponse(url="/mail?msg=메일 발송 성공!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/mail?msg=실패: {str(e)}", status_code=303)

@api_router.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id: return RedirectResponse(url="/login", status_code=303)
    mail_handler = UserMAILHandler(**MAIL_CONFIG)
    success, emails = mail_handler.get_mail_from_nfs(user_id=user_id, INBOX_BASE_PATH=INBOX_BASE_PATH)
    return templates.TemplateResponse("inbox.html", {"request": request, "user_id": user_id, "emails": emails if success else [], "generated_email" : f"{user_id}{allowed_domain}"})

# =====================================================================

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    # 외부 접속 허용(0.0.0.0), 로컬(127.0.0.1)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)