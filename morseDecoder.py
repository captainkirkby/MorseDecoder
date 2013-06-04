import RPi.GPIO as GPIO
import time

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#constants
STANDARD_BOUNCE_TIME = 33
THRESHOLD=0.8
MIN_KEY_TIME=0.20
MIN_DELAY_TIME=0.10

#globals
pressedDownTime = 0
pressedUpTime = 0
pressedDurations = [ ]

def buttonPressed(channel):
	global pressedUpTime
	pressedDuration = time.time() - pressedUpTime
	if pressedDuration <= MIN_DELAY_TIME:
		return
	else:
		print("Button Depressed")
		global pressedDownTime
		pressedDownTime=time.time()
		GPIO.remove_event_detect(23)
		GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(23, GPIO.RISING, callback=buttonReleased)

def buttonReleased(channel):
	global pressedDownTime
	pressedDuration = time.time() - pressedDownTime
	if pressedDuration <= MIN_KEY_TIME:
		return
	else:
		global pressedUpTime
		pressedUpTime = time.time()
		print("Button Released")
		GPIO.remove_event_detect(23)
		GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(23, GPIO.FALLING, callback=buttonPressed)
		print(pressedDuration)

def minimumBounceTime(maxRpm):
	result = 0
	try:
		result = (1.0/float(maxRpm/60.0))*1000*THRESHOLD
	except ZeroDivisionError:
		result = STANDARD_BOUNCE_TIME
	return int(result)

GPIO.add_event_detect(23, GPIO.FALLING,
		callback=buttonPressed,
		bouncetime=minimumBounceTime(900))

try:
	GPIO.wait_for_edge(24, GPIO.FALLING)

except KeyboardInterrupt:
	print("Exiting...")
	GPIO.cleanup()

GPIO.cleanup()
