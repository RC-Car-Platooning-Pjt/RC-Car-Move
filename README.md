# RC-Car-Move

## RC CAR -> GUI MQTT 구조

### JSON 구조
    0. state : 상태 값
    1. 속도 제약 값
    2. y, x 좌표
    3. 0

### 기본 코드 실행

    1. UI 및 MQTT를 통한 원격 조종기 ( node-red 실행 )
        : node-red
    2. MQTT Broker
        : mosquitto -c mosquitto.conf -v
    3. python Move.py -> systectl or bashrc 이용 자동 실행 예정
        : pub 및 sub 설정
    4. 이후 GUI 원격 조종기를 이용한 실시간 조종.