import time
import math
import board
import busio
import adafruit_icm20x
from gpiozero import LED

# -----------------------------
# HARDWARE SETUP
# -----------------------------

i2c = busio.I2C(board.SCL, board.SDA)
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

level_led = LED(24)
north_led = LED(25)

LEVEL_THRESHOLD = 5
NORTH_TOLERANCE = 15

# Measured while breadboard was physically pointing North
HEADING_OFFSET = 255


# -----------------------------
# LEVEL CALIBRATION
# -----------------------------

def calibrate_level(samples=30):
    print("\nLEVEL CALIBRATION")
    print("Place the breadboard flat and keep it still...")

    roll_sum = 0
    pitch_sum = 0
    successful_samples = 0

    while successful_samples < samples:
        try:
            x, y, z = imu.acceleration

            roll = math.degrees(math.atan2(y, z))

            pitch = math.degrees(
                math.atan2(
                    -x,
                    math.sqrt(y * y + z * z)
                )
            )

            roll_sum += roll
            pitch_sum += pitch
            successful_samples += 1

        except OSError as error:
            print(f"I2C error during level calibration: {error}")

        time.sleep(0.1)

    roll_offset = roll_sum / samples
    pitch_offset = pitch_sum / samples

    print(f"Roll offset: {roll_offset:.2f}°")
    print(f"Pitch offset: {pitch_offset:.2f}°")

    return roll_offset, pitch_offset


# -----------------------------
# LEVEL FUNCTIONS
# -----------------------------

def get_tilt(roll_offset, pitch_offset):
    x, y, z = imu.acceleration

    roll = math.degrees(math.atan2(y, z))

    pitch = math.degrees(
        math.atan2(
            -x,
            math.sqrt(y * y + z * z)
        )
    )

    roll -= roll_offset
    pitch -= pitch_offset

    return roll, pitch


def is_level(roll, pitch):
    return (
        abs(roll) <= LEVEL_THRESHOLD
        and abs(pitch) <= LEVEL_THRESHOLD
    )


# -----------------------------
# NORTH FUNCTIONS
# -----------------------------

def get_heading():
    mx, my, mz = imu.magnetic

    raw_heading = math.degrees(
        math.atan2(my, mx)
    ) % 360

    corrected_heading = (
        raw_heading - HEADING_OFFSET
    ) % 360

    return raw_heading, corrected_heading


def is_north(heading):
    return (
        heading <= NORTH_TOLERANCE
        or heading >= 360 - NORTH_TOLERANCE
    )


# -----------------------------
# INITIAL CALIBRATION
# -----------------------------

roll_offset, pitch_offset = calibrate_level()

print("\nSYSTEM RUNNING")
print("Level LED: GPIO24")
print("North LED: GPIO25")
print()


# -----------------------------
# MAIN LOOP
# -----------------------------

while True:
    try:

        # -----------------
        # LEVEL
        # -----------------

        roll, pitch = get_tilt(
            roll_offset,
            pitch_offset
        )

        if is_level(roll, pitch):
            level_led.on()
            level_state = "LEVEL"
        else:
            level_led.off()
            level_state = "TILTED"


        # -----------------
        # NORTH
        # -----------------

        raw_heading, heading = get_heading()

        if is_north(heading):
            north_led.on()
            north_state = "NORTH"
        else:
            north_led.off()
            north_state = "NOT NORTH"


        # -----------------
        # OUTPUT
        # -----------------

        print(
            f"Roll={roll:.1f}° "
            f"Pitch={pitch:.1f}° "
            f"{level_state} | "
            f"Raw={raw_heading:.1f}° "
            f"Heading={heading:.1f}° "
            f"{north_state}"
        )

    except OSError as error:

        print(f"I2C read error: {error}")

        level_led.off()
        north_led.off()

    time.sleep(0.2)
