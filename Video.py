import cv2
import torch
import base64
import asyncio
import numpy as np
from picamera2 import Picamera2
from libcamera import Transform
from Global_Var import G
class VideoStreamer:
    def __init__(self):
        # Picamera2 초기화
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='RC4.pt')
        self.camera = Picamera2()
        self.camera.preview_configuration.main.size = (320, 240)  # 해상도 설정
        self.camera.preview_configuration.main.format = "RGB888"
        self.camera.preview_configuration.transform = Transform(vflip=1, hflip=1)
        self.camera.configure("preview")
        self.camera.start()
        self.convert = {
            "one" : 1,
            "two" : 2,
            "three" : 3
        }
        
        # 프레임 전송 간격 (초)
        self.interval = 0.1

        
    async def start_streaming(self, client):
        try:
            print("스트리밍 시작...")
            while True:
                # 프레임 캡처
                frame = self.camera.capture_array()
                img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                results = self.model(img)

                df = results.pandas().xywh[0]
                for index, row in df.iterrows():
                    class_name = row['name']  # 클래스 이름
                    confidence = row['confidence']  # 신뢰도
                    if confidence > 0.8:
                        client.publish(G.data["TOPIC"] + "/master", self.convert[class_name])
                        G.voiceflag = True

                render_img = np.squeeze(results.render())
                # OpenCV로 이미지를 JPEG로 인코딩
                _, buffer = cv2.imencode('.jpg', render_img, [cv2.IMWRITE_JPEG_QUALITY, 50])
                
                # base64로 인코딩
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # MQTT로 전송
                client.publish(G.data["TOPIC"] + "/video", jpg_as_text)
                
                # 지정된 간격만큼 대기
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("스트리밍 종료")
            self.cleanup(client)
        except Exception as e:
            print(f"에러 발생: {str(e)}")
            self.cleanup(client)
            
    def cleanup(self, client):
        self.camera.stop()
        client.disconnect()

# 스트리머 객체 생성 및 시작
V = VideoStreamer()
