import socket
import mailbox
import os
from email.header import decode_header, make_header

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
        mail_file = os.path.join(INBOX_BASE_PATH, user_id)
        
        if not os.path.exists(mail_file):
            return True, []

        try:
            mbox = mailbox.mbox(mail_file)
            keys = list(mbox.keys())
            
            for key in reversed(keys[-10:]):
                msg = mbox[key]
                
                # Decoding
                def safe_decode_header(header_value):
                    if not header_value:
                        return ""
                    # RFC 2047 
                    return str(make_header(decode_header(header_value)))

                subject = safe_decode_header(msg['subject'])
                sender = safe_decode_header(msg['from'])

                # 본문
                content = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            # charset  (utf-8)
                            charset = part.get_content_charset() or 'utf-8'
                            payload = part.get_payload(decode=True)
                            content = payload.decode(charset, errors='ignore')
                            break
                else:
                    charset = msg.get_content_charset() or 'utf-8'
                    payload = msg.get_payload(decode=True)
                    content = payload.decode(charset, errors='ignore')

                messages.append({
                    "index": key,
                    "from": sender,
                    "subject": subject,
                    "date": msg['date'],
                    "content": content
                })
                
            return True, messages
        
        except Exception as e:
            sentence = f"[WAS server] NFS load error : {str(e)}"
            print(sentence)
            return False, sentence