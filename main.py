
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# autor: Adrian Rutkowski
# cel : zaliczenie TAISM


import sys
from time import sleep
import signal
from gpiozero import LED, Button
from threading import Thread

#IMPORT DO FIREBASE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#from PI_SHT1X import SHT1X
#from RPi.GPIO as GPIO
#from pi-sht1x import SHT1x
from w1thermsensor import W1ThermSensor
#from sht1x.Sht1x import Sht1x
dataPin = 2
clkPin = 3
#sht1x = SHT1x(dataPin, clkPin, SHT1x.GPIO_BOARD)

#temperature = sht1x.read_temperature_C()
#humidity = sht1x.read_humidity()
#dewPoint = sht1x.calculate_dew_point(temperature, humidity)


#INIT
LED = LED(14)
BUTTON = Button(15)

PAHT_CRED = '/home/pi/Downloads/cred.json'
URL_DB = 'https://taism-1699d.firebaseio.com/'

REF_HOME = 'TAISM'
REF_LED = 'LED'
REF_BTTN = 'PRZYCISK'
REF_YLED = 'ZOLTY_LED'
REF_SW1 = 'PRZYCISK1'
REF_TEMP= 'TEMPERATURA'
REF_DS18B20 ='DALLAS'

class IOT():

    def __init__(self):
        cred = credentials.Certificate(PAHT_CRED)
        firebase_admin.initialize_app(cred, {
            'databaseURL': URL_DB
        })

        self.refHome = db.reference(REF_HOME)

        self.estructuraInicialDB()  # solo ejecutar la primera vez

        self.refLed = self.refHome.child(REF_LED)
        self.refYLed = self.refLed.child(REF_YLED)

        self.refBttn = self.refHome.child(REF_BTTN)
        self.refSw1 = self.refBttn.child(REF_SW1)
	self.refT = self.refHome.child(REF_TEMP)
	self.refDS = self.refT.child (REF_DS18B20)

    def estructuraInicialDB(self):
        self.refHome.set({
            'LED': {
                'ZOLTY_LED': True,
            },
            'PRZYCISK': {
                'PRZYCISK1': False,
            },
	    'TEMPERATURA': {
		'DALLAS' : 0,
	    }
        })

    def ledControlGPIO(self, led):
        if led:
            LED.on()
            print('LED ON')
        else:
            LED.off()
            print('LED OFF')

    def led_Start(self):

        E, i = [], 0
	try:
        	led_status = self.refYLed.get();
	except BadStatusLine:
		print "error"
        self.ledControlGPIO(led_status)

        E.append(led_status)

        while True:
            led_actual = self.refYLed.get();
            E.append(led_actual)

            if E[i] != E[-1]:
                self.ledControlGPIO(led_actual)

            del E[0]
            i = i + i
            sleep(0.4)

    def switch_on(self):
        print('Switch On')
 	try:      
 		self.refSw1.set(True)
	except BadStatusLine:
		print" could not fetch "
    def switch_off(self):
        print('Switch Off')
        try:
		self.refSw1.set(False)
	except BadStatusLine:
		print"could not fetch"
    def read_temp(self):
	try:
		self.refDS.set(temperature2)
	except BadStatusLine:
		print"could not fetch"
    def bttn_Start(self):
        print('Start BTN !')
        BUTTON.when_pressed = self.switch_on
        BUTTON.when_released = self.switch_off
    def read_dallas(self):
	sensor = W1ThermSensor()
	while True :
		#temperature3=temperature2
		sensor.set_precision(9)
		temperature2 = sensor.get_temperature()
		self.refDS.set(temperature2)
		#if temperature2 != temperature3:
		#	print ("Temperatura w pokoju {:.1f}".format( temperature2))
		#self.read_temp

print('URUCHOMIONO...')
#print("Temperature: {} Humidity: {} Dew Point: {}".format(temperature, humidity, dewPoint))
#print("Temprature : {}".format(temperature2))
iot=IOT()

subproceso_led = Thread(target=iot.led_Start)
subproceso_led.daemon = True
subproceso_led.start()


subproceso_btn = Thread(target=iot.bttn_Start)
subproceso_btn.daemon = True
subproceso_btn.start()

subproceso_ds =Thread(target=iot.read_dallas)
subproceso_ds.daemon = True
subproceso_ds.start()


signal.pause()
