import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Firebase 초기화
try:
    cred = credentials.Certificate("rc-car-project-90e87-firebase-adminsdk-ypiev-d282df2a55.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase 초기화 성공")
except Exception as e:
    print(f"Firebase 초기화 실패: {e}")

# 로그 추가 함수
def add_log(car_name, event_type):
    try:
        timestamp = datetime.now().isoformat()

        doc_ref = db.collection(car_name).add({
            "Type": event_type,
            "Timestamp": timestamp
        })
        print(f"Firebase 로그 추가 성공: {event_type}")
    except Exception as e:
        print(f"Firebase 로그 추가 실패: {e}")
