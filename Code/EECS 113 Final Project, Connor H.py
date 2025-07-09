#Name:	Connor Hoang
#ID:	2829138

import RPi.GPIO as GPIO
import Freenove_DHT as DHT
import threading
import time
import requests
from datetime import datetime
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep, strftime

done = False #to finish program
#pin assignments
#PIR
PIRsense = 17
PIRLed = 12
#DHT
DHTsense = 27
ACled = 18
Heatled = 23
incButt = 20
decButt = 21
doorButt = 16

#variables
desiredTemp = 80
currTemp = 0
weatherInd = 81
PIRon = False
opening = False #false = closed, true = open


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#setup buttons and pins
def setup():
	#PIR
	GPIO.setup(PIRLed, GPIO.OUT)
	GPIO.setup(PIRsense, GPIO.IN)

	#DHT
	GPIO.setup(DHTsense, GPIO.IN)
	GPIO.setup(ACled, GPIO.OUT)
	GPIO.setup(Heatled, GPIO.OUT)
	GPIO.setup(incButt, GPIO.IN)
	GPIO.setup(decButt, GPIO.IN)
	
	#door
	GPIO.setup(doorButt, GPIO.IN)
	
	#start all LEDs off
	GPIO.output(PIRLed, GPIO.LOW)
	GPIO.output(ACled, GPIO.LOW)
	GPIO.output(Heatled, GPIO.LOW)

def PIRrun():
	global PIRon
	alrOff = True
	while not done:
		if GPIO.input(PIRsense) == GPIO.LOW: # if no PIR readings, then wait 10 seconds before turning off
			count = 10
			while count > 0:
				if GPIO.input(PIRsense) == GPIO.LOW:
					count -= 1
					if not alrOff:
						print(getTime(), 'LIGHTS OFF IN ', count)
						sleep(1)
				else:
					break
					
			if count <= 0:
				GPIO.output(PIRLed, GPIO.LOW)
				if not alrOff: #ensures no print repeat
					print(getTime(), "LIGHTS OFF")
					PIRon = False
					alrOff = True
				else:
					PIRon = False
					alrOff = True
		else: # if there are PIR readings, keep/turn lights on
			GPIO.output(PIRLed, GPIO.HIGH)
			if alrOff: #ensures no print repeat
				print(getTime(), "LIGHTS ON")
				PIRon = True
				alrOff = False
			else:
				PIRon = True
				alrOff = False

def DHTrun():
	global opening
	global weatherInd
	global currTemp
	alrPrinted = False
	dht = DHT.DHT(DHTsense)   #create DHT class object
	# cannot get CIMIS to work
	#resp = requests.get('http://et.water.ca.gov/api/data?appKey=(43ac6ff3-36d5-44b7-8bec-4434abbbe3bd)&targets=75&startDate=2024-05-27&endDate=2024-05-27&dataItems=hly-rel-hum&unitOfMeasure=E')
	#post = resp.float()
	irvHumidity = 78 # static value
	
	while not done:
		for i in range(0,15):            
			chk = dht.readDHT11()     #read DHT11
			if (chk == dht.DHTLIB_OK):      #is DHT11 normal
				#print("\t\t\t|DHT11,OK!")
				#print("\t\t\t|Dr : ", opening)
				break
			sleep(0.3)
		
		if not opening: #If there's no openings, then HVAC on and DHT working
			#fire ex
			#weatherInd = 100
			
			currTemp = (int)((dht.temperature * 1.8) + 32)
			#print("DHT Temp : %dF"%(dhtTemp))
			weatherInd = currTemp + (0.05*irvHumidity)
			#print("Weather Index : %dF"%(weatherInd))
				
			alrPrinted = False
		else: # if opening, then HVAC off 
			GPIO.output(ACled, GPIO.LOW)
			GPIO.output(Heatled, GPIO.LOW)
			if not alrPrinted:
				print(getTime(), "HVAC OFF")
				alrPrinted = True
			

def dispFire(): # Display on term and LCD of fire
	global weatherInd
	lcd.clear()
	lcd.setCursor(0,0)
	lcd.message("FIRE - EVACUATE")
	lcd.setCursor(0,1)
	lcd.message("DR/WINDWS OPEN")
	sleep(3)
	dispHOff()
	dispO()
	for i in range(0,3): # Flash lights
		GPIO.output(Heatled, GPIO.HIGH) #Heater on
		sleep(.5)
		GPIO.output(ACled, GPIO.HIGH) #AC on
		sleep(.5)
		GPIO.output(Heatled, GPIO.LOW) #Heater off
		sleep(.5)
		GPIO.output(ACled, GPIO.LOW) #AC off
		
	
	while weatherInd >= 95:
		weatherInd = weatherInd - 1
		print(getTime()," FIRE TEMP: ", weatherInd, "F")
		sleep(1)
			
	sleep(0.5)	

def dispAC():
	lcd.clear()
	lcd.setCursor(4,0)
	lcd.message("AC is on")
	sleep(3)
	GPIO.output(ACled, GPIO.HIGH) #AC/blue led on
	GPIO.output(Heatled, GPIO.LOW) #Heat/red led on
	lcd.clear()
	sleep(0.5)

def dispHeat():
	lcd.clear()
	lcd.setCursor(2,0)
	lcd.message("Heater is on")
	sleep(3)
	GPIO.output(ACled, GPIO.LOW) #AC/blue led off
	GPIO.output(Heatled, GPIO.HIGH) #Heat/red led on
	lcd.clear()
	sleep(0.5)

def dispHOff():
	lcd.clear()
	lcd.setCursor(2,0)
	lcd.message("HVAC is off")
	sleep(3)
	GPIO.output(ACled, GPIO.LOW) # HVAC off, both leds off
	GPIO.output(Heatled, GPIO.LOW)
	lcd.clear()
	
def dispO():
	lcd.clear()
	
	if opening:
		lcd.setCursor(3,0)
		lcd.message("door/window")
		lcd.setCursor(5,1)
		lcd.message("open!")
	else:
		lcd.setCursor(3,0)
		lcd.message("door/window")
		lcd.setCursor(5,1)
		lcd.message("closed!")
		
	sleep(3)
	lcd.clear()
	sleep(0.5)

def LCDrun():
	global desiredTemp
	global weatherInd
	global opening
	global PIRon
	global currTemp
	
	#makes sure it's not continuously printing in terminal
	dispACAlr = False
	dispHeatAlr = False
	dispOffAlr = False
	dispFireAlr = False
	dispOAlr = False
	
	mcp.output(3,1)
	lcd.begin(16,5)
	while not done:
		#DesiredTemp/CurrTemp
		lcd.setCursor(0,0)
		sleep(1)
		lcd.message("%d/%d"%(desiredTemp, currTemp))
		
		lcd.setCursor(6,0)
		lcd.message(getLCDTime())
		
		#Door/Window open/closed
		lcd.setCursor(12,0)
		if opening:
			if not dispOAlr:
				print(getTime(), "DOOR OPEN")
				dispO()
				dispOAlr = True
			lcd.message("Dr:O")
		else:
			if dispOAlr:
				print(getTime(), "DOOR CLOSED")
				dispO()
				dispOAlr = False
			lcd.message("Dr:C")
		
		
		#HVAC Msgs
		if opening:
			lcd.setCursor(0,1)
			lcd.message("H:OFF ")
			GPIO.output(ACled, GPIO.LOW) # no leds on
			GPIO.output(Heatled, GPIO.LOW)
		else:
			if weatherInd > 95: #fire alarm
				opening = True
				if not dispFireAlr:
					dispFire()
					dispFireAlr = True
					dispOffAlr = False
					dispACAlr = False
					dispHeatAlr = False
			else:
				if weatherInd >= desiredTemp +3: # too hot -> AC on
					if not dispACAlr:
						dispAC()
						print(getTime(), "HVAC AC")
						dispACAlr = True
						dispHeatAlr = False
						dispOffAlr = False
					lcd.setCursor(0,1)
					lcd.message("H:AC ")
				else:
					if weatherInd <= desiredTemp-3: # too cold, heat on
						if not dispHeatAlr:
							dispHeat()
							print(getTime(), "HVAC HEATER")
							dispHeatAlr = True
							dispACAlr = False
							dispOffAlr = False
						lcd.setCursor(0,1)
						lcd.message("H:HEAT")
						GPIO.output(Heatled, GPIO.HIGH) #Heater on
						GPIO.output(ACled, GPIO.LOW)
					else:
						if dispOffAlr:
							dispHOff()
							dispOffAlr = True
							dispACAlr = False
							dispHeatAlr = False
						lcd.setCursor(0,1)
						lcd.message("H:OFF ")
						GPIO.output(ACled, GPIO.LOW) # no leds on
						GPIO.output(Heatled, GPIO.LOW)
						
		#PIR 
		if PIRon:
			lcd.setCursor(11,1)
			lcd.message(" L:ON")
		else:
			lcd.setCursor(11,1)
			lcd.message("L:OFF")

def getTime():
	return datetime.now().strftime('%H:%M:%S')	
	
def getLCDTime():
	return datetime.now().strftime('%H:%M')			
			
def inc(): # increase desired temp
	global desiredTemp
	sleep(0.2)
	if desiredTemp < 95:
		desiredTemp += 1
		print("Desired Temp : %dF"%(desiredTemp))

def dec(): # decrease desired temp
	global desiredTemp
	sleep(0.2)
	if desiredTemp > 65:
		desiredTemp -= 1
		print("Desired Temp : %dF"%(desiredTemp))

def toggleDr(): # toggle door/window opening
	global opening
	if opening:
		opening = False
	else:
		opening = True	
	#print("Dr changed: ", opening)
	
def buttons(): # when buttons are clicked, trigger variable changes
	while not done:
		if GPIO.input(doorButt)==GPIO.LOW:
			toggleDr()
			sleep(.5)
			
		if GPIO.input(incButt)==GPIO.LOW:
			inc()
			sleep(0.2)
		else:
			if GPIO.input(decButt)==GPIO.LOW:
				dec()
				sleep(0.2)

def destroy():
	lcd.clear()
	GPIO.cleanup()
	sleep(1)
	
if __name__ == '__main__':
	print('Program Starting...')
	setup()
	
	PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
	PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
	try:
		mcp = PCF8574_GPIO(PCF8574_address)
	except:
		try:
			mcp = PCF8574_GPIO(PCF8574A_address)
		except:
			print ('I2C Address Error !')
			exit(1)
	lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
	
	try:
		buttons = threading.Thread(target=buttons, daemon = True)
		PIRthread = threading.Thread(target=PIRrun, daemon = True)
		DHTthread = threading.Thread(target=DHTrun, daemon = True)
		LCDthread = threading.Thread(target=LCDrun)
		
		buttons.start()
		PIRthread.start()
		DHTthread.start()
		LCDthread.start()
		
		buttons.join()
		PIRthread.join()
		DHTthread.join()
		LCDthread.join()
		
	except KeyboardInterrupt:
		done = True
		destroy()
