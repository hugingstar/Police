from fastapi import FastAPI, Request, Form, Cookie, Depends, Query
from urllib.parse import quote
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from typing import Optional, List
import os
from CRUD_handler import UserDBHandler
from MAIL_handler import UserMAILHandler
import re
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import date
import json


# FastAPI
app = FastAPI(title="Kojel Private equity Fund")
# 컨테이너 내부 경로를 입력
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
    sentence = f"[WAS server] INBOX/SENTBOX folder create error"
    print(sentence)

# Mail server config
MAIL_CONFIG = {
    "MAIL_SERVER_IP" : "10.22.0.2",  # 실제 메일 서버 IP로 변경하세요
    "MAIL_SEND_PORT" : 25,
    "MAIL_RECEIVE_PORT" : 110,
    "MAIL_SERVER_PORT" : 9999,          # 메일 서버 수신 포트
    "INBOX_BASE_PATH" : INBOX_BASE_PATH,
    "SENT_MAIL_PATH" : SENT_MAIL_PATH
}

# Database information
DB_CONFIG = {

    "host": "mariadb-service", 
    "port": 3306, 
    "user": "root", 
    "password": "P@ssw0rd", 
    "db_name": "userdb", 
    "tbl_name": "members"
}

# Monitoring
DATA_ROOT_DIR = "/root/Data"
STOCK_LIST_ROOT = "/root/market"
MARKETS = ["KOSPI", "KOSDAQ", "NASDAQ", "NYSE"]
ALL_COLUMNS = ["name", "open", "high", "low", "close", "volume", "RSI", "CCI", "MACD", "ADX", "Drawdown"] # 가독성을 위해 요약

# *********************************************************************
# Extra functions
def get_current_user(user_id: Optional[str] = Cookie(None)):
    """쿠키에서 user_id를 읽어 로그인 여부 확인"""
    return user_id

# *********************************************************************
#Front-end
# =====================================================================

# First main page

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request, 
                    msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
# =====================================================================

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@app.post("/login")
async def login(user_id: str = Form(...), password: str = Form(...)):
    db_handler = UserDBHandler(**DB_CONFIG)
    success, result = db_handler.verify_login(user_id, password)
    
    # # # 디버깅시 로그인 비활성화
    # message = quote(f"{result}님, 환영합니다!")
    # redirect_response = RedirectResponse(url=f"/users?msg={message}", status_code=303)
    # redirect_response.set_cookie(key="user_id", value=user_id, httponly=True)
    # return redirect_response

    if success:
        # result(사용자명)에 한글이 포함될 수 있으므로 quote로 감쌉니다.
        message = quote(f"{result}님, 환영합니다!")
        redirect_response = RedirectResponse(url=f"/users?msg={message}", status_code=303)
        redirect_response.set_cookie(key="user_id", value=user_id, httponly=True)
        return redirect_response
    else:
        error_msg = quote(str(result))
        return RedirectResponse(url=f"/login?msg={error_msg}", status_code=303)

# =====================================================================
# Insert page
@app.get("/insert", response_class=HTMLResponse)
async def insert_form(request: Request, msg: str = None):
    return templates.TemplateResponse("insert.html", {"request": request, "msg": msg})

@app.post("/insert")
async def create_user(
    user_id: str = Form(...), 
    password: str = Form(...),
    username: str = Form(...), 
    email: str = Form(None),  # HTML에서 readonly로 넘어옴
    birthday: str = Form(None), 
    age: int = Form(0),
    department: str = Form(None), 
    emp_number: str = Form(...)
):  

    # 1. 이메일 강제 생성 (보안 강화)
    # 프론트엔드에서 수정했을 가능성을 배제하고, 서버에서 user_id 기반으로 다시 만듭니다.
    generated_email = f"{user_id}{allowed_domain}"

    # 만약 넘어온 email과 생성된 email이 다르다면 (비정상적인 접근 방지)
    if email and email != generated_email:
        message = "가입 실패: 이메일 형식이 올바르지 않습니다."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    # 2. 사번(Employee number) 형식 검증
    emp_pattern = r"^C\d{6}$"
    if not re.match(emp_pattern, emp_number):
        message = "가입 실패: 인증번호는 'C'로 시작하는 7자리여야 합니다."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    # 3. 비밀번호 복잡도 검증
    password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
    if not re.match(password_pattern, password):
        message = "가입 실패: 비밀번호 규정(대/소문자, 특수문자 포함 8자 이상)을 확인하세요."
        return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

    # 4. 메일 서버 계정 생성 및 DB 저장
    message = "가입 실패: 알 수 없는 오류" # 초기 메시지 설정

    try:
        mail_handler = UserMAILHandler(**MAIL_CONFIG)
        mail_success = mail_handler.add_mail_user(user_id, password) 

        if mail_success:
            input_data = (user_id, password, username, generated_email, birthday, age, department, emp_number)
            db_handler = UserDBHandler(**DB_CONFIG, inputData=input_data)
            success, db_message = db_handler.execute_insert()
            message = db_message
        else:
            message = "가입 실패: 메일 서버 통신 불가로 계정을 생성할 수 없습니다."
            print(message)
    except Exception as e:
        message = f"가입 실패: 서버 오류 발생 ({str(e)})"
        print(message)
    # 결과 페이지로 리다이렉트
    return RedirectResponse(url=f"/insert?msg={message}", status_code=303)

# Monitoring
@app.get("/stock", response_class=HTMLResponse)
async def stock_main(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=" + quote("로그인이 필요합니다."), status_code=303)
    
    generated_email = f"{user_id}{allowed_domain}"
    return templates.TemplateResponse("stock.html", {
        "request": request,
        "user_id": user_id,
        "email": generated_email,
        "all_columns": ALL_COLUMNS,
        "markets": MARKETS,
        "tables": {},
        "counts": {"bull": 0, "bear": 0, "sell": 0},
        "chart_data": "{}",
        "selected_date": date.today().isoformat(),
        "selected_market": "KOSPI"
    })

@app.post("/stock", response_class=HTMLResponse)
async def search_stock_data(
    request: Request,
    target_date: str = Form(...),
    market: str = Form(...),
    selected_cols: List[str] = Form(None),
    user_id: str = Depends(get_current_user)
):
    if not user_id: 
        return RedirectResponse(url="/login", status_code=303)
    
    generated_email = f"{user_id}{allowed_domain}"
    
    if not selected_cols: selected_cols = ["name", "open", "close", "volume", "RSI"]

    # 종목 코드 매핑 로직
    stock_map = {}
    map_file_path = os.path.join(STOCK_LIST_ROOT, market, "stock_list.csv")
    if os.path.exists(map_file_path):
        ref_df = pd.read_csv(map_file_path, dtype={'code': str, 'symbol': str})
        code_col = 'code' if 'code' in ref_df.columns else 'symbol'
        stock_map = dict(zip(ref_df['name'], ref_df[code_col]))

    folder_path = os.path.join(DATA_ROOT_DIR, market, "B1Sheet", target_date)
    data_types = {"bull": "df_bull", "bear": "df_bear", "sell": "df_sell"}
    tables_html, counts, chart_data = {}, {}, {}

    for key, filename_base in data_types.items():
        file_path = os.path.join(folder_path, f"{filename_base}.csv")
        chart_data[key] = []
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, encoding='cp949')
                if set(['name', 'RSI5', 'CCI5']).issubset(df.columns):
                    chart_data[key] = df[['name', 'RSI5', 'CCI5']].fillna(0).to_dict(orient='records')
                
                valid_cols = [c for c in selected_cols if c in df.columns]
                df_filtered = df[valid_cols].copy()
                counts[key] = len(df_filtered)

                if 'name' in df_filtered.columns:
                    def create_link(name):
                        code = stock_map.get(name)
                        if not code: return name
                        base_url = "https://finance.naver.com/item/main.naver?code=" if market in ["KOSPI", "KOSDAQ"] else "https://finance.yahoo.com/quote/"
                        return f'<a href="{base_url}{code}" target="_blank" style="color: #2563eb; text-decoration: none;">{name}</a>'
                    df_filtered['name'] = df_filtered['name'].apply(create_link)

                tables_html[key] = df_filtered.to_html(classes="table table-hover table-bordered", index=False, escape=False)
            except Exception as e:
                tables_html[key] = f"에러: {str(e)}"
                counts[key] = 0
        else:
            tables_html[key] = "데이터 없음"
            counts[key] = 0

    return templates.TemplateResponse("stock.html", {
        "request": request,
        "user_id": user_id,
        "email": generated_email,
        "all_columns": ALL_COLUMNS,
        "markets": MARKETS,
        "tables": tables_html,
        "counts": counts,
        "chart_data": json.dumps(chart_data),
        "selected_date": target_date,
        "selected_market": market
    })


# =====================================================================
# user list page
@app.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request, 
    msg: Optional[str] = Query(None),  # Optional 및 Query(None) 명시
    dept: Optional[str] = Query(None), 
    name: Optional[str] = Query(None), 
    user_id: str = Depends(get_current_user)
):
    if not user_id:
        return RedirectResponse(url="/login?msg=" + quote("로그인이 필요합니다."), status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    db_handler = UserDBHandler(**DB_CONFIG)
    
    # DB 핸들러의 execute_select가 dept, name 인자를 받도록 수정되어 있어야 합니다.
    success, result = db_handler.execute_select(dept=dept, name=name)

    table_html = None
    if success:
        # result가 데이터프레임인지 확인
        if result is not None and not result.empty:
            table_html = result.to_html(classes='table table-striped table-hover', index=False)
        else:
            if dept or name:
                msg = "검색 조건에 일치하는 정보가 없습니다."
            else:
                msg = "등록된 회원 정보가 없습니다."

    else:
        msg = f"데이터베이스 에러: {result}"
        print(msg)
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "table": table_html, 
        "user_id": user_id,
        "email" : generated_email,
        "msg": msg
    })

# =====================================================================
# Send Mail page
@app.get("/mail", response_class=HTMLResponse)
async def mail_page(request: Request, msg: str = None, user_id: str = Depends(get_current_user)):

    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    return templates.TemplateResponse("mail.html", {"request": request, "msg": msg, "user_id": user_id, "email" : generated_email})

@app.post("/send_mail")
async def send_mail(
    receiver: str = Form(...),
    subject: str = Form(...),
    content: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    try:

        # 메일 객체 생성 및 발송 (기존 로직 동일)
        message = MIMEMultipart()
        message["From"] = generated_email
        message["To"] = receiver
        message["Subject"] = subject
        message.attach(MIMEText(content, "plain"))
        with smtplib.SMTP(MAIL_CONFIG["MAIL_SERVER_IP"], MAIL_CONFIG["MAIL_SEND_PORT"]) as server:
            server.send_message(message)

        # --- 수정된 저장 로직: Content 추가 ---
        sent_file = os.path.join(SENT_MAIL_PATH, f"{user_id}")
        with open(sent_file, "a", encoding="utf-8") as f:
            f.write(f"To: {receiver}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Date: {pd.Timestamp.now()}\n")
            f.write(f"Content: {content}\n") # 본문 추가
            f.write("---\n") # 구분자
        return RedirectResponse(url="/mail?msg=메일 발송 성공!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/mail?msg=메일 발송 실패: {str(e)}", status_code=303)

# =====================================================================
# Inbox page
@app.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    mail_handler = UserMAILHandler(**MAIL_CONFIG)

    # NFS 파일에서 직접 읽기
    success, emails = mail_handler.get_mail_from_nfs(user_id=user_id, INBOX_BASE_PATH=INBOX_BASE_PATH)

    return templates.TemplateResponse("inbox.html", {
        "request": request, 
        "user_id": user_id, 
        "emails": emails if success else [],
        "msg": None if success else emails,
        "generated_email" : generated_email
    })



# =====================================================================
# Sent page
@app.get("/sent", response_class=HTMLResponse)
async def sent_page(request: Request, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    generated_email = f"{user_id}{allowed_domain}"
    sent_emails = []
    sent_file = os.path.join(SENT_MAIL_PATH, f"{user_id}")

    if os.path.exists(sent_file):
        try:
            with open(sent_file, "r", encoding="utf-8") as f:
                content_all = f.read().strip()
                if content_all:
                    # '---' 구분자로 메일 단위 분리
                    mail_blocks = content_all.split("---\n")
                    for block in mail_blocks:
                        if not block.strip(): continue
                        lines = block.strip().split("\n")
                        email_item = {
                            "to": "알 수 없음",
                            "subject": "(제목 없음)",
                            "date": "-",
                            "content": "", # 본문 필드 추가
                            "status": "성공"
                        }

                        # 각 줄을 돌며 데이터 파싱
                        for line in lines:
                            if line.startswith("To: "):
                                email_item["to"] = line.replace("To: ", "").strip()
                            elif line.startswith("Subject: "):
                                email_item["subject"] = line.replace("Subject: ", "").strip()
                            elif line.startswith("Date: "):
                                email_item["date"] = line.replace("Date: ", "").strip()[:19]
                            elif line.startswith("Content: "):
                                # Content: 이후의 모든 내용을 가져옴
                                email_item["content"] = line.replace("Content: ", "").strip()  
                        sent_emails.append(email_item)
            sent_emails.reverse()
        except Exception as e:
            print(f"발신함 로드 중 오류 발생: {e}")

    return templates.TemplateResponse("sent.html", {
        "request": request, 
        "user_id": user_id,
        "generated_email" : generated_email,
        "emails": sent_emails
    })

# =====================================================================
# Delete page
@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request, msg: str = None, user_id: str = Depends(get_current_user)):
    if not user_id:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    return templates.TemplateResponse("delete.html", {"request": request, "msg": msg})

@app.post("/delete")
async def delete_user(
    user_id_cookie: str = Depends(get_current_user),
    user_id: str = Form(...), 
    password: str = Form(...), 
    emp_number: str = Form(...)):
    if not user_id_cookie:
        return RedirectResponse(url="/login?msg=로그인이 필요합니다.", status_code=303)
    # 메일 서버에 계정 삭제 요청 먼저 수행
    mail_success = del_to_mail_server(user_id, password)
    if not mail_success:
        # 메일 생성이 실패하면 DB에 넣지 않고 즉시 리턴
        return RedirectResponse(url="/?msg=삭제 실패!", status_code=303)

    if mail_success:
        db_handler = UserDBHandler(**DB_CONFIG, inputData=(user_id, password, emp_number))
        success, message = db_handler.execute_delete()
    return RedirectResponse(url=f"/delete?msg={message}", status_code=303)

# =====================================================================

# Logout
@app.get("/logout")
async def logout():
    """쿠키를 삭제하여 로그아웃 처리"""
    message = quote("로그아웃 되었습니다.")
    # 로그인 페이지로 리다이렉트하면서 쿠키 삭제
    response = RedirectResponse(url=f"/login?msg={message}", status_code=303)
    response.delete_cookie(key="user_id")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)