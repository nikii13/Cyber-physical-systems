import time
import board
import busio
import adafruit_icm20x

#en el lab usamso acelerometro y magnetometro en el mismo componente IMU, tb tiene giroscopio
i2c = busio.I2C(board.SCL, board.SDA)
#El acelerómetro detecta la gravedad. Si la placa está plana, la gravedad cae casi completamente sobre un solo eje
#El magnetómetro, en cambio, funciona parecido a una brújula digital. Mide el campo magnético terrestre
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

while True:
    ax, ay, az = imu.acceleration
    gx, gy, gz = imu.gyro
    mx, my, mz = imu.magnetic

    print("Acceleration:")
    print(f"X={ax:.2f}  Y={ay:.2f}  Z={az:.2f}")

    print("Magnetic field:")
    print(f"X={mx:.2f}  Y={my:.2f}  Z={mz:.2f}")

    print()

    time.sleep(1)
