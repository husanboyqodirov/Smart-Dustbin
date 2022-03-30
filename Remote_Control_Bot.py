#!/usr/bin/env python

# coded with love by Husanboy Qodirov

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import RPi.GPIO as GPIO
from gpiozero import Servo, Buzzer
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import sys
import Adafruit_DHT
from picamera import PiCamera

# Servo Motor
factory = PiGPIOFactory()
myCorrection=0
maxPW=(2.0+myCorrection)/1000
minPW=(1.0-myCorrection)/1000
servo = Servo(26, pin_factory=factory,  initial_value=1, min_pulse_width=minPW,max_pulse_width=maxPW)

# Active Buzzer
buzzer = Buzzer(4)
blindMode = True

# RGB LED
RedLED = 22
GreenLED = 27
BlueLED = 17
GPIO.setup(BlueLED, GPIO.OUT)
GPIO.setup(GreenLED, GPIO.OUT)
GPIO.setup(RedLED, GPIO.OUT)

GPIO.setmode(GPIO.BCM)
photoresistor = 16
GPIO.setup(photoresistor,GPIO.IN,pull_up_down=GPIO.PUD_UP)

camera = PiCamera()
playing_melody = False

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
    
def buzz(noteFreq, duration):
    halveWaveTime = 1 / (noteFreq * 2 )
    waves = int(duration * noteFreq)
    for i in range(waves):
       buzzer.on()
       time.sleep(halveWaveTime)
       buzzer.off()
       time.sleep(halveWaveTime)
       

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Welcome back Husanboy! Send me your command to control dustbin or type /help_me to learn:')


def help_me(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('MANUAL for Commands\n--------------------\n'+
                              '/help_me - Read manual for commands\n'+
                              '/open - Open cover of dustbin\n'+
                              '/temp - Check temperature in your room\n'+
                              '/picture - Take picture of your room\n'+
                              '/play_melody - Play melody\n'+
                              '/check_light - Check light in your room')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Invalid command! Type /help_me to learn more.')

def open_cover(update: Update, context: CallbackContext) -> None:
    servo.min()
    if blindMode:
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
    rgbLED()
    update.message.reply_text('Cover opened!')
    time.sleep(3)
    servo.max()
    if blindMode:
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
    rgbLED()
    update.message.reply_text('Cover closed!')

def temperature(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Getting temperature... Please wait')
    humidity, temperature = Adafruit_DHT.read_retry(11, 25)
    update.message.reply_text("Temp: {0:0.1f} C  Humidity: {1:0.1f} %" .format(temperature, humidity))

def take_picture(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Taking picture... Please wait')
    camera.capture('image.jpg')
    chat_id=update.effective_chat.id
    context.bot.send_document(chat_id=chat_id, document=open('image.jpg', 'rb'))

def play_melody(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Melody started playing...')
    t=0
    notes=[262,294,330,262,262,294,330,262,330,349,392,330,349,392,392,440,392,349,330,262,392,440,392,349,330,262,262,196,262,262,196,262]
    duration=[0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.5,0.25,0.25,0.5,0.125,0.125,0.125,0.125,0.25,0.25,0.125,0.125,0.125,0.125,0.25,0.25,0.25,0.25,0.5,0.25,0.25,0.5]
    playing_melody = True
    for n in notes:
        if playing_melody:
            buzz(n, duration[t])
            time.sleep(duration[t] *0.1)
            t+=1
    update.message.reply_text('Melody stopped playing')
    
def check_light(update: Update, context: CallbackContext) -> None:
    state = GPIO.input(photoresistor)
    if state == 0:
        update.message.reply_text("It is Light in your room!\n")
    else:
        update.message.reply_text("It is Dark in your room!\n")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass my bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help_me", help_me))
    dispatcher.add_handler(CommandHandler("open", open_cover))
    dispatcher.add_handler(CommandHandler("temp", temperature))
    dispatcher.add_handler(CommandHandler("picture", take_picture))
    dispatcher.add_handler(CommandHandler("play_melody", play_melody))
    dispatcher.add_handler(CommandHandler("check_light", check_light))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
