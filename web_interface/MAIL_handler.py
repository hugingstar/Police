import socket
import mailbox
import os

class UserMAILHandler():
    def __init__(self, 
                 MAIL_SERVER_IP, # Mail server ip
                 MAIL_SERVER_PORT, # Mail server port
                 INBOX_BASE_PATH, # Inbox path
                 **kwargs
                 ):
        
        self.MAIL_SERVER_IP = MAIL_SERVER_IP
        self.MAIL_SERVER_PORT = MAIL_SERVER_PORT
        self.INBOX_BASE_PATH = INBOX_BASE_PATH

    def add_mail_user(self, user_id, password):
        """Add user"""
        try:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 3초 타임아웃
                s.connect((self.MAIL_SERVER_IP, self.MAIL_SERVER_PORT))
                # 전송 형식: adduser:아이디:비밀번호
                message = f"useradd:{user_id}:{password}"
                s.sendall(message.encode('utf-8'))
                return True
            
        except Exception as e:
            sentence = f"[WAS server] Add user error : {e}"
            print(sentence)
            return False

    def del_mail_user(self, user_id, password):
        """Delete user"""
        try:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 3 sec timeout
                s.connect((self.MAIL_SERVER_IP, self.MAIL_SERVER_PORT))
                # 전송 형식: deluser:user_id:password
                message = f"userdel:{user_id}:{password}"
                s.sendall(message.encode('utf-8'))
                return True
            
        except Exception as e:
            sentence = f"[WAS server] Delete user error : {e}"
            print(sentence)
            return False

    def get_mail_from_nfs(self, user_id, INBOX_BASE_PATH):

        messages = []

        # Inbox directory
        mail_file = os.path.join(INBOX_BASE_PATH, user_id)
        
        if not os.path.exists(mail_file):
            return True, [] # 사서함 파일이 없으면 빈 목록 반환

        try:
            # mailbox
            mbox = mailbox.mbox(mail_file)
            
            # Latest mail 10
            keys = list(mbox.keys())
            for key in reversed(keys[-10:]):
                msg = mbox[key]
                
                # Text extraction
                content = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode(errors='ignore')
                            break
                else:
                    content = msg.get_payload(decode=True).decode(errors='ignore')

                # Mail contents
                messages.append({
                    "index": key,
                    "from": msg['from'],
                    "subject": msg['subject'],
                    "date": msg['date'],
                    "content": content
                })
            return True, messages
        
        except Exception as e:
            sentence = f"[WAS server] NFS load error : {str(e)}"
            print(sentence)
            return False, sentence