import socket
import os

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 포트가 이미 사용 중일 때 발생하는 에러를 방지하는 옵션
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(1)
    
    print("--- 메일 계정 생성 리스너가 가동되었습니다 (9999 포트) ---")
    
    while True:
        # 1. 여기서 다음 접속자가 올 때까지 프로그램이 딱 멈춰서 기다립니다.
        conn, addr = server_socket.accept() 
        
        try:
            data = conn.recv(1024).decode('utf-8')
            if data.startswith("useradd"):
                _, uid, pwd = data.split(':')
                
                # 2. 계정 생성 실행
                res1 = os.system(f"useradd -m {uid}")
                res2 = os.system(f"echo '{uid}:{pwd}' | chpasswd")
                
                if res1 == 0 and res2 == 0:
                    print(f"계정 생성 완료: {uid}")
                    # 3. 웹 서버에 성공했다고 알려줌 (매우 중요!)
                    conn.sendall("SUCCESS".encode('utf-8'))
                else:
                    print(f"계정 생성 실패 (명령어 오류): {uid}")
                    conn.sendall("FAIL".encode('utf-8'))
                 
            elif data.startswith("userdel"):
                _, uid, pwd = data.split(':')

                user_check = os.system(f"id {uid} > /dev/null 2>&1")
                
                if user_check != 0:
                    print(f"삭제 실패: {uid} 사용자가 없습니다.")
                    conn.sendall("FAIL".encode('utf-8'))
                
                else: 
                    res = os.system(f"userdel -rf {uid}")
        
                    if res == 0:
                        print(f"계정 삭제 완료: {uid}")
                        conn.sendall("SUCCESS".encode('utf-8'))
                    else:
                        print(f"계정 삭제 실패 (명령어 오류): {uid}")
                        conn.sendall("FAIL".encode('utf-8'))

        except Exception as e:
            print(f"에러 발생: {e}")
            conn.sendall(f"ERROR:{e}".encode('utf-8'))
            
        finally:
            conn.close()

if __name__ == "__main__":
    start_server()
