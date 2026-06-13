from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

from gpiozero import LED, Buzzer, DistanceSensor, DigitalInputDevice
import board
import adafruit_dht
from RPLCD.i2c import CharLCD
from datetime import datetime
from time import sleep

#Throttle
last_lcd_update = 0
LCD_INTERVAL = 2

# =========================
# GPIO PIN CONFIGURATION
# =========================

# LEDs
ENTRY_LED_PIN = 17
ALARM_LED_PIN = 27

# Buzzer
BUZZER_PIN = 22

# PIR motion sensor
MOTION_SENSOR_PIN = 23

# Fire and gas sensors
FIRE_SENSOR_PIN = 24
GAS_SENSOR_PIN = 25

# Temperature sensor
# DHT11 or DHT22 data pin
TEMP_SENSOR_PIN = board.D4

# Ultrasonic sensors
ULTRASONIC_SENSOR = [
    {
        "name": "Front Door",
        "trigger": 5,
        "echo": 6
    }
]

# Temperature danger limit
TEMP_LIMIT = 35

# Distance limit for ultrasonic detection
DISTANCE_LIMIT_CM = 50

#To Prevent Spam For The Motion Sensor
motion_triggered = False

# =========================
# DEVICE SETUP
# =========================

entry_led = LED(ENTRY_LED_PIN)
alarm_led = LED(ALARM_LED_PIN)
buzzer = Buzzer(BUZZER_PIN, active_high=False)

sleep(0.2)
motion_sensor = DigitalInputDevice(MOTION_SENSOR_PIN, pull_up=False)

sleep(0.2)
fire_sensor = DigitalInputDevice(FIRE_SENSOR_PIN, pull_up=False)

sleep(0.2)
gas_sensor = DigitalInputDevice(GAS_SENSOR_PIN, pull_up=False)

temperature_sensor = adafruit_dht.DHT11(TEMP_SENSOR_PIN)

ultrasonic_sensors = []
for sensor in ULTRASONIC_SENSOR:
    ultrasonic_sensors.append({
        "name": sensor["name"],
        "device": DistanceSensor(
            echo=sensor["echo"],
            trigger=sensor["trigger"],
            max_distance=4
        )
    })
    sleep(0.2)

# LCD setup
lcd = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2
)


# =========================
# HELPER FUNCTIONS
# =========================

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def lcd_message(line1, line2=""):
    global last_lcd_update

    now = datetime.now().timestamp()
    if now - last_lcd_update < LCD_INTERVAL:
        return

    lcd.clear()
    lcd.write_string(line1[:16])

    if line2:
        lcd.crlf()
        lcd.write_string(line2[:16])

    last_lcd_update = now

def entry_detected(source):
    current_time = get_time()

    print(f"{source}: User entered at {current_time}")

    lcd_message("User entered", current_time)

    entry_led.on()
    sleep(3)
    entry_led.off()


def start_alarm(reason):
    print(f"ALARM: {reason}")

    lcd_message("WARNING!", reason)

    alarm_led.blink(on_time=0.3, off_time=0.3)
    buzzer.on()


def stop_alarm():
    alarm_led.off()
    buzzer.off()


# =========================
# MAIN PROGRAM
# =========================
print("Smart Home System Started...")
lcd_message("Smart Home", "System Ready")
sleep(2)

alarm_active = False

try:
    while True:
        danger_detected = False
        danger_reason = ""

        # =========================
        # Motion Sensor Logic
        # =========================
        if motion_sensor.value and not motion_triggered:
            entry_detected("Motion Sensor")
            motion_triggered = True

        if not motion_sensor.value:
            motion_triggered = False

        # =========================
        # Ultrasonic Sensor Logic
        # =========================
        for sensor in ultrasonic_sensors:
            distance_cm = sensor["device"].distance * 100

            if 0 < distance_cm < DISTANCE_LIMIT_CM:
                entry_detected(sensor["name"])
                sleep(0.3)

        # =========================
        # Temperature Sensor Logic
        # =========================
        try:
            temperature = temperature_sensor.temperature

            humidity = temperature_sensor.humidity

            if temperature is not None:
                print(f"Temperature: {temperature}C | Humidity: {humidity}%")
                if temperature >= TEMP_LIMIT:
                    danger_detected = True
                    danger_reason = "High Temp"

        except RuntimeError:
            # DHT sensors sometimes fail to read, this is normal
            pass

        # =========================
        # Fire Sensor Logic
        # =========================
        if fire_sensor.value == 0:
            danger_detected = True
            danger_reason = "Fire Detected"

        # =========================
        # Gas Sensor Logic
        # =========================
        if gas_sensor.value == 0:
            danger_detected = True
            danger_reason = "Gas Detected"

        # =========================
        # Alarm Control
        # =========================
        if danger_detected:
            if not alarm_active:
                start_alarm(danger_reason)
                alarm_active = True
        else:
            if alarm_active:
                stop_alarm()
                lcd_message("Smart Home", "Safe")
                alarm_active = False

        sleep(0.5)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    stop_alarm()
    entry_led.off()
    lcd.clear()
    lcd.write_string("System Stopped")
    temperature_sensor.exit()