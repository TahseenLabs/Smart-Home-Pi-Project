"""
This Raspberry Pi code was developed by newbiely.com
This Raspberry Pi code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-ultrasonic-sensor-led
"""


import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins for the ultrasonic sensor
TRIG_PIN = 14
ECHO_PIN = 15

# Define the GPIO pin for the LED
LED_PIN = 16

# Set up the ultrasonic sensor pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Set up the LED pin as an output
GPIO.setup(LED_PIN, GPIO.OUT)

# Define the distance threshold in cm (adjust as needed)
DISTANCE_THRESHOLD = 20 # 20 cm

def get_distance():
    # Send a trigger signal
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # Wait for the echo response
    pulse_start = time.time()
    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pulse_end = time.time()

    # Calculate the distance in centimeters
    pulse_duration = pulse_end - pulse_start
    speed_of_sound = 34300  # Speed of sound in cm/s
    distance = (pulse_duration * speed_of_sound) / 2

    return distance

try:
    while True:
        # Get the distance from the ultrasonic sensor
        distance = get_distance()
        print("Distance:", distance, "cm")

        # If the distance is below the threshold, turn on the LED
        if distance < DISTANCE_THRESHOLD:
            print("Distance below threshold. Turning on the LED.")
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            print("Distance above threshold. Turning off the LED.")
            GPIO.output(LED_PIN, GPIO.LOW)

        # Add a small delay to avoid excessive readings
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up the GPIO on exiting the script
    GPIO.cleanup()
