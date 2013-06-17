import RPi.GPIO as GPIO
from decoder import decode
import time

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#constants
STANDARD_BOUNCE_TIME = 60
MIN_KEY_TIME = 0.15
MIN_DELAY_TIME = 0.10
LEARNING_CYCLE = 8

#morse constants
DIT = 1
DAH = 2

#gap constants
NEW_MORSE_CHARACTER = 3
NEW_LETTER = 4
NEW_WORD = 5

#globals
pressedDownTime = 0
pressedUpTime = 0
pressedDurations = [0.25, 0.5]

resultingMorse = []
resultingText = ""


def buttonPressed(channel):
    """Callback called when GPIO detects button is pressed"""
    global pressedUpTime
    pressedDuration = time.time() - pressedUpTime
    #software switch deboucing
    if pressedDuration <= MIN_DELAY_TIME:
        return
    else:
        #if button is pressed
        print("Button Depressed")
        #check that this is not the first time
        if pressedUpTime != 0:
            #use gap to determine if new morse character, new letter, or new word.
            gapDuration = time.time() - pressedUpTime
            #get gap
            gap = detectGap(gapDuration)
            print(morseToString(gap))
        global pressedDownTime
        pressedDownTime = time.time()
        #reset event detection
        GPIO.remove_event_detect(23)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(23, GPIO.RISING, callback=buttonReleased)


def buttonReleased(channel):
    print(resultingText)
    """Callback called when GPIO detects button is released"""
    global pressedDownTime
    pressedDuration = time.time() - pressedDownTime
    #software switch debouncing
    if pressedDuration <= MIN_KEY_TIME:
        return
    else:
        #if button is actually released
        print("Button Released")
        global pressedUpTime
        pressedUpTime = time.time()
        #reset event detection
        GPIO.remove_event_detect(23)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=buttonPressed)
        #get the character
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


def detectGap(duration):
    """Determines if a gap represents a new morse character,
    a new letter, or a new word.  An inter-element gap is the
    same length as a dit, an character separation gap is the
    same length as a dah (3 dits), and the word separation gap
    is the same length as 7 dits."""
    global pressedDurations
    pressedDurationsCopy = list(pressedDurations)
    pressedDurationsCopy.sort()
    #find highest (TODO:non-outlier) duration and assume it is DAH
    dahBenchmark = pressedDurationsCopy[len(pressedDurationsCopy)-1]
    #calculate ideal dit as half the duration of the dah benchmark
    ditBenchmark = dahBenchmark/2
    #compare duration to benchmarks
    if duration <= ((ditBenchmark+dahBenchmark)/2):
        return NEW_MORSE_CHARACTER
    elif duration <= (2*ditBenchmark+dahBenchmark):
        return NEW_LETTER
    else:
        return NEW_WORD


def morseToString(morseChar):
    if morseChar == DIT:
        return "DIT"
    elif morseChar == DAH:
        return "DAH"
    elif morseChar == NEW_MORSE_CHARACTER:
        return "New Morse Character"
    elif morseChar == NEW_LETTER:
        return "New Letter"
    elif morseChar == NEW_WORD:
        return "New Word"
    return "?"


def addToResult(morseChar):
    global resultingText
    if(morseChar == DIT or morseChar == DAH or morseChar == NEW_MORSE_CHARACTER):
        #if DIT, DAH or NEW_MORSE_CHARACTER add to morse result
        resultingMorse.append(morseChar)
    elif(morseChar == NEW_LETTER):
        #if new letter, add to morse result and compute completed
        #letter and add to result string
        resultingMorse.append(morseChar)
        previousChar = getPreviousCharFromMorse(resultingMorse)
        print(previousChar)
        resultingText += decode(previousChar)
    elif(morseChar == NEW_WORD):
        #if new word, add to morse result and add space to result string
        resultingMorse.append(morseChar)
        resultingText += " "
    else:
        #if none of the above, add a question mark to the results
        resultingMorse.append("?")
        resultingText += "?"


def getPreviousCharFromMorse(morseCharList):
    #first find last two instances of NEW_LETTER
    mutableList = list(morseCharList)
    mutableList.reverse()
    lowerLimit = mutableList.index(NEW_LETTER)
    mutableList[lowerLimit] = 0
    upperLimit = mutableList.index(NEW_LETTER)
    sublist = mutableList[lowerLimit + 1:upperLimit]
    sublist.reverse()
    return sublist


GPIO.add_event_detect(23, GPIO.FALLING,
                      callback=buttonPressed,
                      bouncetime=STANDARD_BOUNCE_TIME)

try:
    GPIO.wait_for_edge(24, GPIO.FALLING)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()

GPIO.cleanup()
