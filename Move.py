from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
import asyncio
import paho.mqtt.client as mqtt
import json
from functools import partial


data = ""

try:
    with open('basedata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")
except PermissionError:
    print("파일을 읽을 권한이 없습니다.")
except:
    print("파일을 읽는 중 오류가 발생했습니다.")

# 모터 초기설정
mh = Raspi_MotorHAT(addr=0x6f)
motor1 = mh.getMotor(2)
speed = 125
motor1.setSpeed(speed)

# 서보 초기설정
servo = mh._pwm
servo.setPWMFreq(60)
servoCH = 0
SERVO_PULSE_MAX = int(data["rightv"])
SERVO_PULSE_MIN = int(data["leftv"])

# MQTT 설정
MQTT_BROKER = data["IP"]
MQTT_PORT = data["PORT"]
MQTT_TOPIC = data["TOPIC"]

# 제어 함수들
def go():
    motor1.run(Raspi_MotorHAT.BACKWARD)

def back():
    motor1.run(Raspi_MotorHAT.FORWARD)

def stop():
    motor1.run(Raspi_MotorHAT.RELEASE)

def speed_change(v):
    global speed
    motor1.setSpeed(v)

def steer(angle):
    if angle <= -60: angle = -60
    if angle >= 60: angle = 60
    pulse_time = SERVO_PULSE_MIN + (SERVO_PULSE_MAX - SERVO_PULSE_MIN) // 180 * (angle + 90)
    servo.setPWM(servoCH, 0, pulse_time)

def steer_right():
    steer(30)

def steer_left():
    steer(-30)

def steer_center():
    steer(0)

def control_car(x, y, maxsp, dir):
    """
    x: -1 (왼쪽) ~ 1 (오른쪽)
    y: -1 (후진) ~ 1 (전진)
    """
    global speed  # 전역 변수 speed 사용
    global data
    # 설정값
    MIN_SPEED = 0
    MAX_SPEED = maxsp
    DEADZONE = data["deadzone"]
    MIN_ANGLE = -50
    MAX_ANGLE = 80
    speed_value = 0
    angle = 0
    try:
        #데드존 체크
        if abs(float(x)) < DEADZONE and abs(float(y)) < DEADZONE:
            motor1.run(Raspi_MotorHAT.RELEASE)
            steer(0)
            return 0
        
        # 속도 제어 (y축)
        if abs(float(y)) > DEADZONE:
            speed_value = int(abs(float(y)) * (MAX_SPEED - MIN_SPEED) + MIN_SPEED)
            speed_value = min(speed_value, MAX_SPEED)
            motor1.setSpeed(speed_value)
            if float(y) > 0:
                motor1.run(Raspi_MotorHAT.BACKWARD)
            else:
                motor1.run(Raspi_MotorHAT.FORWARD)
        else:
            motor1.run(Raspi_MotorHAT.RELEASE)
        
        # 회전 제어 (x축)
        if not dir:
            steer(0)
            return speed_value
        
        if abs(x) > DEADZONE:
            angle = x * MAX_ANGLE
            # 속도에 따른 회전 각도 조정
            angle = angle * (1 - abs(y) * 0.5)
            steer(int(angle))
        else:
            steer(0)
        
        print(f"Speed: {speed_value if abs(float(y)) > DEADZONE else 0}, Angle: {angle if abs(float(x)) > DEADZONE else 0}")
        return speed_value
    except Exception as e:
        print(f"제어 오류: {e}")
        return 0

def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

class MQTTController:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.loop = asyncio.get_event_loop()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")

    def on_message(self, client, userdata, msg):
        try:
            command_str = msg.payload.decode()
            cmd = json.loads(command_str)
            print(cmd)
            if cmd['state'] == "stop":
                stop()
            elif cmd['state'] == "move":
               result = control_car(cmd['x'], cmd['y'], cmd['maxsp'], cmd['dir'])
               self.client.publish(data["TOPIC"] + "/speed", result)
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT Broker")
        if rc != 0:
            print(f"Unexpected disconnect. Will auto-reconnect")

    async def start(self):
        try:
            # Connect to broker
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            self.client.publish(data["DASHPUB"], "차량 " + data["NAME"] + " 연결됨")

            # Start MQTT loop in a separate thread
            self.client.loop_start()
            
            print("MQTT Controller started")
            

            # Keep the program running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Error in MQTT Controller: {e}")
        finally:
            self.client.loop_stop()
            self.client.publish(data["DASHPUB"], "차량 " + data["NAME"] + " 연결 해제됨")
            self.client.disconnect()
            motor1.run(Raspi_MotorHAT.RELEASE)

async def main():
    try:
        print("Starting RC Vehicle Control System...")
        controller = MQTTController()
        await controller.start()
        
    except KeyboardInterrupt:
        print('\nShutting down by user request...')
    except Exception as e:
        print(f'\nUnexpected error: {e}')
    finally:
        motor1.run(Raspi_MotorHAT.RELEASE)

if __name__ == '__main__':
    asyncio.run(main())