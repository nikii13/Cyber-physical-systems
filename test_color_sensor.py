import time
import board
import busio
import adafruit_tcs34725

# I2C connection
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
sensor = adafruit_tcs34725.TCS34725(i2c)

print("Reading color sensor for 2 minutes...")

start_time = time.time()

while time.time() - start_time < 120:
    r, g, b = sensor.color_rgb_bytes
    color_temp = sensor.color_temperature
    lux = sensor.lux

    print(f"R={r} G={g} B={b} | Temp={color_temp}K | Lux={lux:.2f}")

    time.sleep(1)

print("Finished.")
