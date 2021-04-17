import RPi.GPIO as GPIO
import os
import time
import json
import redis

configFileLocation = os.getenv('alarm_config_location') 
if not configFileLocation :
    configFileLocation = '../appsettings.json'
    
configFile = open(configFileLocation)
config = json.load(configFile)
buzzerPins = config["Buzzers"]["Pins"]

# INIT BUZZER pins
GPIO.setmode(GPIO.BCM)
for idx, pin in enumerate(buzzerPins) :
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


r = redis.Redis(host=config['Redis']['ip'], port=config['Redis']['port'], db=0, password=config['Redis']['password'])
r_pubsub = r.pubsub()
current_alarm_state = 0

def raise_Alarm(buzzeridx):
    GPIO.output(buzzerPins[buzzeridx], GPIO.HIGH)
    time.sleep(2)
    GPIO.output(buzzerPins[buzzeridx], GPIO.LOW)
    time.sleep(1)
    
def stop_Alarm(buzzeridx):
    GPIO.output(buzzerPins[buzzeridx], GPIO.LOW)
    time.sleep(1)

def my_callback(self):
    global current_alarm_state
    
    alarmStatus = int(self['data'])
    print ('RAISE ALARM :' + str(alarmStatus))
    current_alarm_state = alarmStatus
    
r_pubsub.subscribe(**{'RAISE_ALARM':my_callback})
r_pubsub.run_in_thread(sleep_time=0.001)

while True:
    time.sleep(1)
    if current_alarm_state == 1:
        raise_Alarm(0)
    elif current_alarm_state == 0:
        stop_Alarm(0)
    
