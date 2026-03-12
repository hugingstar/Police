import logging #파이썬 표준 로깅 모듈 
from logging.handlers import SysLogHandler #syslog(/dev/Log)로 로그 전송용 핸들러 

def setup_logger():
    # "fastapi" 라는 이름의 로거 생성 
    # 여러 파일에서 동일한 로거를 공유하기 위함 
    logger = logging.getLogger("fastapi")

    # WARNING 이상 로그만 처리 (WARNING, ERROR, CRITICAL) 
    # INFO, DEBUG 로그 무시 
    logger.setLevel(logging.ERROR)

    # 리눅스 로컬 syslog 유닉스 소켓 (/dev/log) 
    # rsyslog가 이 소켓을 수신 
    syslog = SysLogHandler(address="/dev/log")

    # syslog로 전송될 로그 포맷 
    formatter = logging.Formatter(
        "fastapi: [%(levelname)s] %(message)s"
    )

    # 포맷을 syslog 핸들러에 적용 
    syslog.setFormatter(formatter)

    # 로거에 syslog 핸들러 연결 
    logger.addHandler(syslog)

    # 설정 완료된 로거 반환
    return logger
