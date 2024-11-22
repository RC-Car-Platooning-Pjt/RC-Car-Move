# RC-Car-Move

## RC CAR -> GUI MQTT 구조

### JSON 구조
    0. state : 상태 값
    1. 속도 제약 값
    2. y, x 좌표
    3. dir 값
    4. masternum 값


### 기본 코드 실행

    1. UI 및 MQTT를 통한 원격 조종기 ( node-red 실행 )
        : node-red
    2. MQTT Broker C:\Program Files\mosquitto
        : mosquitto -c mosquitto.conf -v
    3. python Move.py -> systectl or bashrc 이용 자동 실행 예정
        : pub 및 sub 설정
    4. 이후 GUI 원격 조종기를 이용한 실시간 조종.
    5. mqtt.py가 main임.


### 코드 변경 사항

    1. 기본적인 MQTT 코드 및 이를 통한 Node-Red 조이스틱을 활용하여 실시간 원격 조종
        : 조이스틱의 X, Y 좌표를 반환받아 속도와 각도로 변경
    2. Node-Red의 반환값을 Json으로 설정, Json 중 State를 통해 실행할 함수를 결정함.
        : stop, move, pairing, pairend 함수를 통해 각 상태 구현
    3. Node-Red의 구조를 Watch dog을 이용하여 안정성 상승
        : 좌표 입력이 1초간 없을 경우 자동차 중지
    4. pairend 함수는 pairflag를 통해 현상태 확인
        : pairflag 1 : slave, 0 : master
    5. 복잡한 코드를 줄이기 위한 모듈화 진행
        : 전역변수를 관리하기 위한 싱글톤 패턴 진행, 센서(RC CAR), MQTT 통신, Video 4가지의 코드로 분리함. 