# coded with love by Husanboy Qodirov

#Libraries
import RPi.GPIO as GPIO
from gpiozero import Servo, Buzzer
from gpiozero.pins.pigpio import PiGPIOFactory
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

coverClosed = True
 
# Ultrasonic Sensor
GPIO_TRIGGER = 18
GPIO_ECHO = 23
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Servo Motor
factory = PiGPIOFactory()
myCorrection=0
maxPW=(2.0+myCorrection)/1000
minPW=(1.0-myCorrection)/1000
servo = Servo(26, pin_factory=factory,  initial_value=1, min_pulse_width=minPW,max_pulse_width=maxPW)

# Active Buzzer
buzzer = Buzzer(4)
blindMode = False

# RGB LED
RedLED = 22
GreenLED = 27
BlueLED = 17
GPIO.setup(BlueLED, GPIO.OUT)
GPIO.setup(GreenLED, GPIO.OUT)
GPIO.setup(RedLED, GPIO.OUT)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def rgbLED():
    GPIO.output(RedLED, True)
    GPIO.output(GreenLED, False)
    GPIO.output(BlueLED, False)
    time.sleep(0.1)
    
    GPIO.output(RedLED, False)
    GPIO.output(GreenLED, True)
    GPIO.output(BlueLED, False)
    time.sleep(0.2)
    
    GPIO.output(RedLED, False)
    GPIO.output(GreenLED, False)
    GPIO.output(BlueLED, True)
    time.sleep(0.2)
    
    GPIO.output(RedLED, False)
    GPIO.output(GreenLED, False)
    GPIO.output(BlueLED, False)
    time.sleep(0.2)
    
def rgbLEDOff():
    GPIO.output(RedLED, False)
    GPIO.output(GreenLED, False)
    GPIO.output(BlueLED, False)
    
rgbLEDOff()
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            if (dist < 50):
                if coverClosed:
                    servo.min()
                    coverClosed = False
                    if blindMode:
                        buzzer.on()
                        time.sleep(0.5)
                        buzzer.off()
                    rgbLED()
                time.sleep(1)
                
            else:
                if not(coverClosed):
                    servo.max()
                    coverClosed = True
                    if blindMode:
                        buzzer.on()
                        time.sleep(0.5)
                        buzzer.off()
                    rgbLED()
            time.sleep(0.1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        
