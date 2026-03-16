from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
import requests

# 서버 주소 (실제 서버 PC의 내부 IP로 수정하세요)
SERVER_URL = "http://192.168.0.100:8000" 

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.label = MDLabel(
            text="Kojel PE Fund Login",
            halign="center",
            font_style="H4"
        )
        
        self.user_id = MDTextField(
            hint_text="아이디를 입력하세요",
            icon_right="account"
        )
        
        self.password = MDTextField(
            hint_text="비밀번호를 입력하세요",
            password=True,
            icon_right="key"
        )
        
        self.login_btn = MDRaisedButton(
            text="로그인",
            pos_hint={"center_x": .5},
            on_release=self.attempt_login
        )

        layout.add_widget(self.label)
        layout.add_widget(self.user_id)
        layout.add_widget(self.password)
        layout.add_widget(self.login_btn)
        self.add_widget(layout)

    def attempt_login(self, instance):
        payload = {
            "user_id": self.user_id.text,
            "password": self.password.text
        }
        
        try:
            # FastAPI /login 엔드포인트에 Form 데이터 전송
            response = requests.post(f"{SERVER_URL}/login", data=payload, allow_redirects=False)
            
            # 쿠키나 리다이렉트 여부로 로그인 성공 판단
            if response.status_code == 303: 
                self.label.text = "로그인 성공!"
                self.label.theme_text_color = "Custom"
                self.label.text_color = (0, 1, 0, 1)
                # 이후 Stock 화면으로 전환 로직 추가 가능
            else:
                self.label.text = "로그인 실패: 정보를 확인하세요."
                self.label.theme_text_color = "Error"
                
        except Exception as e:
            self.label.text = "서버 연결 불가"
            print(e)

class KojelApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return LoginScreen()

if __name__ == "__main__":
    KojelApp().run()