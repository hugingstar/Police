import pymysql
import pandas as pd

class UserDBHandler():
    def __init__(self, host, port, user, password, db_name, tbl_name, inputData=None, **kwargs):
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.tbl_name = tbl_name
        self.inputData = inputData
        self.conn = None
        

    def get_connection(self):
        return pymysql.connect(
            host=self.host, port=self.port,
            user=self.user, password=self.password, 
            db=self.db_name, charset='utf8mb4'
        )

    def execute_insert(self):
        """enroll information into database"""
        try:
            self.conn = self.get_connection()
            with self.conn.cursor() as cursor:
                query = f"""
                        INSERT INTO {self.tbl_name} 
                        (id, password, username, email, birthday, age, department, emp_number)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """
                cursor.execute(query, self.inputData)
                self.conn.commit()

                sentence = f"[WAS server] Sucess add user"
                # print(sentence)

                return True, "회원 정보 입력 완료!"

        except Exception as e:
                # MySQL/MariaDB의 경우 중복 키 에러 코드는 1062입니다.
                if "1062" in str(e) or "Duplicate entry" in str(e):
                    sentence = f"[WAS server] Duplicated data input : {str(e)}"
                    print(sentence)
                    return False, "이미 등록된 정보(ID 또는 사원번호)입니다."
                # 2. 그 외의 기타 에러 처리
                sentence = f"[WAS server] Database error : {str(e)}"
                print(sentence)
                return False, sentence
        
        finally:
            if self.conn:
                self.conn.close()
    
    def execute_select(self, dept=None, name=None):
        """부서 또는 이름을 조건으로 데이터를 조회 (없으면 전체 조회)"""
        try:
            with self.get_connection() as conn:
                # 기본 쿼리
                query = f"SELECT username, department, email FROM {self.tbl_name}"
                conditions = []
                params = []

                # 부서 검색 조건 추가
                if dept:
                    conditions.append("department LIKE %s")
                    params.append(f"%{dept}%")
                
                # 이름(username) 검색 조건 추가
                if name:
                    conditions.append("username LIKE %s")
                    params.append(f"%{name}%")

                # 조건이 있다면 WHERE 절 추가
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += ";"

                # Pandas read_sql 사용 (params 전달)
                df = pd.read_sql(query, conn, params=params)
                return True, df
                
        except Exception as e:
            sentence = f"[WAS server] List page error : {str(e)}"
            return False, sentence

    def execute_delete(self):
        """delete information into database"""
        try:
            self.conn = self.get_connection()
            with self.conn.cursor() as cursor:
                query = f"""
                        DELETE FROM {self.tbl_name} 
                        WHERE id=%s AND password=%s AND emp_number=%s;
                        """
                cursor.execute(query, self.inputData)
                
                # Message
                affected_rows = cursor.rowcount
            
                if affected_rows > 0:
                    self.conn.commit()
                    return True, f"{self.inputData[0]} ({self.inputData[2]}) 사원 정보 삭제 완료!"
                else:
                    # 삭제된 데이터가 없으면 입력 정보가 틀린 것임
                    return False, "삭제 실패: 일치하는 회원 정보(ID/비밀번호/사번)가 없습니다."

        except Exception as e:
            sentence = f"[WAS server] Delete page error : {str(e)}"
            print(sentence)
            return False, sentence
        
        finally:
            if self.conn: self.conn.close()

    def verify_login(self, user_id, password):
        """로그인 정보 확인"""
        try:
            self.conn = self.get_connection()
            with self.conn.cursor() as cursor:
                # ID와 비밀번호가 일치하는 사용자 조회
                query = f"SELECT username FROM {self.tbl_name} WHERE id=%s AND password=%s"
                cursor.execute(query, (user_id, password))
                result = cursor.fetchone()
                
                if result:
                    return True, result[0]  # 로그인 성공 (사용자 이름 반환)
                else:
                    return False, "아이디 또는 비밀번호가 일치하지 않습니다."
        except Exception as e:
            sentence = f"[WAS server] Login page error : {str(e)}"
            print(sentence)
            return False, sentence
        
        finally:
            if self.conn: self.conn.close()