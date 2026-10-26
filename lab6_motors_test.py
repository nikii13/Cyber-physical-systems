from gpiozero import Motor
from time import sleep

motor_a = Motor(forward=12, backward=18)
motor_b = Motor(forward=13, backward=19)

try:
    print("Motor A forward")
    motor_a.forward(0.25)
    sleep(1)
    motor_a.stop()

    sleep(1)

    print("Motor A backward")
    motor_a.backward(0.25)
    sleep(1)
    motor_a.stop()

    sleep(1)

    print("Motor B forward")
    motor_b.forward(0.25)
    sleep(1)
    motor_b.stop()

    sleep(1)

    print("Motor B backward")
    motor_b.backward(0.25)
    sleep(1)
    motor_b.stop()

finally:
    motor_a.stop()
    motor_b.stop()

print("Done")
