import asyncio
import paho.mqtt.client as mqtt
from Global_Var import G
from Motor_Control import MC
from Video import V
import json
MQTT_BROKER = G.data["IP"]
MQTT_PORT = G.data["PORT"]
MQTT_TOPIC = G.data["TOPIC"]


class MQTTController:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.loop = asyncio.get_event_loop()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")
        print()
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")

    def on_message(self, client, userdata, msg):
        try:
            command_str = msg.payload.decode()
            cmd = json.loads(command_str)
            G.update_glocmd(cmd)
            print(cmd)
            if cmd['state'] == "stop":
                MC.stop()
            elif cmd['state'] == "move":
               result = MC.control_car(cmd['x'], cmd['y'], cmd['maxsp'], cmd['dir'])
               self.client.publish(G.data["TOPIC"] + "/speed", result)
            elif cmd['state'] == "pairing":
                self.client.unsubscribe(MQTT_TOPIC)
                self.client.subscribe(MQTT_TOPIC[0:-1] + str(cmd['masternum']))
            elif cmd['state'] == "pairend":
                self.client.unsubscribe(MQTT_TOPIC[0:-1] + str(cmd['masternum']))
                self.client.subscribe(MQTT_TOPIC)
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
            self.client.publish(G.data["DASHPUB"], "차량 " + G.data["NAME"] + " 연결됨")

            # Start MQTT loop in a separate thread
            self.client.loop_start()
            print("MQTT Controller started")
            asyncio.create_task(MC.Ultra())
            print("Distance Sensor started")
            asyncio.create_task(V.start_streaming(self.client))
            # Keep the program running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Error in MQTT Controller: {e}")
        finally:
            self.client.loop_stop()
            self.client.publish(G.data["DASHPUB"], "차량 " + G.data["NAME"] + " 연결 해제됨")
            self.client.disconnect()
            MC.stop()

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
        MC.stop()

if __name__ == '__main__':
    asyncio.run(main())