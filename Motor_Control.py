from base.Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from gpiozero import DistanceSensor
import RPi.GPIO as GPIO
from Global_Var import G
import asyncio
class MotorController:
    def __init__(self):
        #모터 초기설정
        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.motor1 = self.mh.getMotor(2)
        self.speed = 125
        self.motor1.setSpeed(self.speed)
        print(G.data)
        # 서보 초기 설정
        self.servo = self.mh._pwm
        self.servo.setPWMFreq(60)
        self.servoCH = 0
        self.SERVO_PULSE_MAX = int(G.data["rightv"])
        self.SERVO_PULSE_MIN = int(G.data["leftv"])

        #초음파센서
        self.ultrasound = DistanceSensor(echo=15, trigger=14)
        self.ultralimit = float(G.data["ultralimit"])

        #LED센서
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17,GPIO.OUT)

    def ledon(self):
        GPIO.output(17,True)
    def ledoff(self):
        GPIO.output(17,False)
    
    #모터 함수
    def go(self):
        self.motor1.run(Raspi_MotorHAT.BACKWARD)

    def back(self):
        self.motor1.run(Raspi_MotorHAT.FORWARD)

    def stop(self):
        self.motor1.run(Raspi_MotorHAT.RELEASE)

    def control_car(self, x, y, maxsp, dir):
        # 설정값
        MIN_SPEED = 0
        MAX_SPEED = maxsp
        DEADZONE = G.data["deadzone"]
        MIN_ANGLE = -50
        MAX_ANGLE = 80
        speed_value = 0
        angle = 0
        try:
            #데드존 체크
            if abs(float(x)) < DEADZONE and abs(float(y)) < DEADZONE:
                self.stop()
                self.steer(0)
                return 0
            
            # 속도 제어 (y축)
            if abs(float(y)) > DEADZONE:
                speed_value = int(abs(float(y)) * (MAX_SPEED - MIN_SPEED) + MIN_SPEED)
                speed_value = min(speed_value, MAX_SPEED)
                self.motor1.setSpeed(speed_value)
                if float(y) > 0:
                    if G.distance > self.ultralimit:
                        self.go()
                else:
                    self.back()
            else:
                self.stop()
            
            # 회전 제어 (x축)
            if not dir:
                self.steer(0)
                return speed_value
            
            if abs(x) > DEADZONE:
                angle = x * MAX_ANGLE
                # 속도에 따른 회전 각도 조정
                angle = angle * (1 - abs(y) * 0.5)
                self.steer(int(angle))
            else:
                self.steer(0)
            
            print(f"Speed: {speed_value if abs(float(y)) > DEADZONE else 0}, Angle: {angle if abs(float(x)) > DEADZONE else 0}")
            return speed_value
        except Exception as e:
            print(f"제어 오류: {e}")
            return 0

    # 서브모터 함수     
    def steer(self,angle):
        if angle <= -60: angle = -60
        if angle >= 60: angle = 60
        pulse_time = self.SERVO_PULSE_MIN + (self.SERVO_PULSE_MAX - self.SERVO_PULSE_MIN) // 180 * (angle + 90)
        self.servo.setPWM(self.servoCH, 0, pulse_time)

    # 초음파센서 함수
    async def Ultra(self):
        while True:
            try:
                distance = self.ultrasound.distance
                G.update_distance(distance)
                if(distance < self.ultralimit):
                    if G.glocmd['state']=="move" and G.glocmd['y'] > 0:
                        self.stop()
                        print("비상! 비상! 비상! 긴급정지!")
                        G.gptdata['emergency']+=1
                if distance is None:
                    distance = 10
                    G.update_distance(distance)
                    print("초음파 센서 값을 읽을 수 없음.")
            except GPIOzeroError as e:
                print(f"GPIO 에러: {e}")
            except Exception as e:
                print(f"기타 에러: {e}")
            await asyncio.sleep(0.5)

MC = MotorController()