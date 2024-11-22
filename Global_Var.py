# global_vars.py
import json

class GlobalVars:
    instance = None  # 클래스 변수로 인스턴스 저장
    
    def __new__(cls):
        # 인스턴스가 없으면 생성, 있으면 기존 인스턴스 반환
        if cls.instance is None:
            cls.instance = super(GlobalVars, cls).__new__(cls)
            # 초기화 진행
            cls.instance.data = ""
            cls.instance.distance = 10
            cls.instance.glocmd = {
                'state': "move",
                'y': 10
            }
            cls.instance.load_data()
        return cls.instance

    def load_data(self):
        try:
            with open('basedata.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다.")
        except PermissionError:
            print("파일을 읽을 권한이 없습니다.")
        except:
            print("파일을 읽는 중 오류가 발생했습니다.")

    def update_distance(self, new_distance):
        self.distance = new_distance

    def update_glocmd(self, new_cmd):
        self.glocmd = new_cmd

# 싱글톤 인스턴스 생성
G = GlobalVars()