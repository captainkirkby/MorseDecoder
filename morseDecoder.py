import RPi.GPIO as GPIO
import time

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#constants
STANDARD_BOUNCE_TIME = 60
MIN_KEY_TIME=0.20
MIN_DELAY_TIME=0.10
LEARNING_CYCLE = 8

#morse constants
DIT=1
DAH=2

#globals
pressedDownTime = 0
pressedUpTime = 0
pressedDurations = [ 0.3, 0.6 ]

def buttonPressed(channel):
    """Callback called when GPIO detects button is pressed"""
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
    """Callback called when GPIO detects button is released"""
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
        
        morseChar = detectCharacter(pressedDuration)
        print(morseToString(morseChar))
        
        #record the last few durations
        global pressedDurations
        if len(pressedDurations) >= LEARNING_CYCLE:
            #remove last item
            del pressedDurations[(len(pressedDurations)-1)]
        
        pressedDurations.append(pressedDuration)
        print(pressedDuration)
    
def detectCharacter(duration):
    """Determines if a duration represents a DIT or a DAH"""
    global pressedDurations
    pressedDurationsCopy = list(pressedDurations)
    pressedDurationsCopy.sort()
    #find highest (TODO:non-outlier) duration and assume it is DAH
    dahBenchmark = pressedDurationsCopy[len(pressedDurationsCopy)-1]
    
    #calculate ideal dit as half the duration of the dah benchmark
    ditBenchmark = dahBenchmark/2
    
    #compare duration to benchmarks
    if duration <= ((ditBenchmark+dahBenchmark)/2):
        return DIT
    else:
        return DAH

def morseToString(morseChar):
    if morseChar == DIT: return "DIT"
    elif morseChar == DAH: return "DAH"
    return "?"

GPIO.add_event_detect(23, GPIO.FALLING,
        callback=buttonPressed,
        bouncetime=STANDARD_BOUNCE_TIME)

try:
    GPIO.wait_for_edge(24, GPIO.FALLING)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()

GPIO.cleanup()
