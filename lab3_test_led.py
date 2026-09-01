import time
import math
import board
import busio
import adafruit_icm20x
from gpiozero import LED

# I2C
i2c = busio.I2C(board.SCL, board.SDA)
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

# LEDs
north_led = LED(25)
level_led = LED(24)

LEVEL_THRESHOLD = 5


def get_tilt():
    x, y, z = imu.acceleration

    roll = math.degrees(math.atan2(y, z))

    pitch = math.degrees(
        math.atan2(-x, math.sqrt(y * y + z * z))
    )

    return roll, pitch


def is_level(roll, pitch):
    return (
        abs(roll) < LEVEL_THRESHOLD
        and abs(pitch) < LEVEL_THRESHOLD
    )


while True:

    roll, pitch = get_tilt()

    if is_level(roll, pitch):
        level_led.on()
        state = "LEVEL"
    else:
        level_led.off()
        state = "TILTED"

    # North LED is not implemented yet
    north_led.off()

    print(
        f"Roll={roll:.1f}° "
        f"Pitch={pitch:.1f}° "
        f"{state}"
    )

    time.sleep(0.1)
