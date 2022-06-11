from htu21 import HTU21
'sudo apt-get install i2c-tools python-smbus'
from time import sleep
import time
import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용
import os

htu = HTU21()


SERVO_MAX_DUTY    = 10.5   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY    = 2.5    # 서보의 최소(0도) 위치의 주기

GPIO.setmode(GPIO.BOARD)        # GPIO 설정
GPIO.setup(12, GPIO.OUT)  # 서보핀 출력으로 설정

servo = GPIO.PWM(12, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다
    
    
time_sleep = 0.7
    
def setServoPos(degree):
    if degree > 180:
        degree = 180
        
    elif degree < 0:
        degree = 0

    duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)

    servo.ChangeDutyCycle(duty)

def fileWrite(temp, humid):

    file_url = '/var/www/html/index.html'
    os.system("sudo chmod 777 {file_url}".format(file_url=file_url))
    
    if flag==1:
        state_aircon = 'ON'
    else :
        state_aircon = 'OFF'
    if mode == 0:
        state_mode = '자동'
    else:
        state_mode = '수동'
        
    data = """
    <!DOCTYPE html>
    <html lang="ko" dir="ltr">
        <head>
            <meta charset="utf-8">
            <title>juno_final</title>
        </head>
        <body>
            <h2>현재 온도</h2>
                %d
            <h2>현재 습도</h2>
                %d
            <h2>작동 유무</h2>
                %s
            <h2>작동 방식</h2>
                %s
        </body>
        <meta http-equiv="refresh" content="3">
    </html>
    """%(temp,humid, state_aircon, state_mode)
    
    write_file = open(file_url, 'w')
    write_file.write(data)
    write_file.close()

    os.system("sudo chmod 744 {file_url}".format(file_url=file_url))


mode = 0


state = 'off'

flag = 0;

print('출근했습니다')

while 1:
    mode = int(input('MODE를 선택하세요(0 자동 / 1 수동/ 2 종료) : '))
    
    if(mode == 0): #자동 모드
        crit_temp = int(input('기준 온도를 입력하세요'))
        while 1:
            temperature = htu.read_temperature()
            humidity = htu.read_humidity()
            fileWrite(temperature, humidity)
            if flag==1 and temperature <crit_temp:
                setServoPos(180)
                sleep(time_sleep)
                setServoPos(0)
                flag = 0
                
            elif flag==0 and temperature >= crit_temp:
                setServoPos(180)
                sleep(time_sleep)
                setServoPos(0)
                flag = 1
            print('tmep  = %d\nhumid = %d\n'%(temperature, humidity))
            sleep(3)
                

    elif mode == 1:
        while 1:
            setServoPos(0)
            state = input('on / off / info / quit: ').lower()
            temperature = htu.read_temperature()
            humidity = htu.read_humidity()
            if state == 'on':
                if flag == 1:
                    print('켜져있습니다')
                else:
                    setServoPos(180)
                    sleep(time_sleep)
                    setServoPos(0)
                    flag = 1
                
            elif state == 'off':
                if flag == 0:
                    print('꺼져있습니다')
                else:
                    setServoPos(180)
                    sleep(time_sleep)
                    setServoPos(0)
                    flag = 0
            
            elif state == 'info':
                print('temp : %.2f'%temperature)
                print('humid: %.2f'%humidity)

                if flag == 0:
                    print('현재 OFF')
                if flag == 1:
                    print('현재 ON')
                
            elif state == 'quit':
                break
            
            else:
                print('잘못 입력했습니다')
                print('')
                continue
            fileWrite(temperature, humidity)
            print('')

    elif mode == 2:
        print('종료')
        break
    

    
servo.stop()
GPIO.cleanup()
