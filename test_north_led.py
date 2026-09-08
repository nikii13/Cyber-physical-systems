import time
import math
import board
import busio
import adafruit_icm20x
from gpiozero import LED

i2c = busio.I2C(board.SCL, board.SDA)
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

north_led = LED(25)

NORTH_TOLERANCE = 15

while True:
    mx, my, mz = imu.magnetic

    heading = math.degrees(math.atan2(my, mx))

    if heading < 0:
        heading += 360

    # North is close to 0° / 360°
    is_north = (
        heading <= NORTH_TOLERANCE
        or heading >= 360 - NORTH_TOLERANCE
    )

    if is_north:
        north_led.on()
        state = "NORTH"
    else:
        north_led.off()
        state = "NOT NORTH"

    print(
        f"X={mx:.2f} Y={my:.2f} Z={mz:.2f} "
        f"Heading={heading:.1f}° {state}"
    )

    time.sleep(0.2)
