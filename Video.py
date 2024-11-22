import cv2
import base64
import asyncio
from picamera2 import Picamera2
from libcamera import Transform

class VideoStreamer:
    def __init__(self):
        # Picamera2 초기화
        self.camera = Picamera2()
        self.camera.preview_configuration.main.size = (320, 240)  # 해상도 설정
        self.camera.preview_configuration.main.format = "RGB888"
        self.camera.preview_configuration.transform = Transform(vflip=1, hflip=1)
        self.camera.configure("preview")
        self.camera.start()
        
        # 프레임 전송 간격 (초)
        self.interval = 0.1
        
    async def start_streaming(self, client, topic):
        try:
            print("스트리밍 시작...")
            while True:
                # 프레임 캡처
                frame = self.camera.capture_array()
                
                # OpenCV로 이미지를 JPEG로 인코딩
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                
                # base64로 인코딩
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # MQTT로 전송
                client.publish(self.topic, jpg_as_text)
                
                # 지정된 간격만큼 대기
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("스트리밍 종료")
            self.cleanup()
        except Exception as e:
            print(f"에러 발생: {str(e)}")
            self.cleanup()
            
    def cleanup(self):
        self.camera.stop()
        self.client.disconnect()

# 스트리머 객체 생성 및 시작
V = VideoStreamer()
V.start_streaming()