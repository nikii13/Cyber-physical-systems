from gpiozero import Motor, DigitalInputDevice
from time import sleep

# Motors
motor_a = Motor(forward=12, backward=18)
motor_b = Motor(forward=13, backward=19)

# Encoders - no internal pull-up/down
pins = {
    17: DigitalInputDevice(17, pull_up=None, active_state=True),
    27: DigitalInputDevice(27, pull_up=None, active_state=True),
    22: DigitalInputDevice(22, pull_up=None, active_state=True),
    23: DigitalInputDevice(23, pull_up=None, active_state=True),}

counts = {17: 0, 27: 0, 22: 0, 23: 0}


def make_counter(pin):
    def count():
        counts[pin] += 1
    return count


for pin, device in pins.items():
    callback = make_counter(pin)
    device.when_activated = callback
    device.when_deactivated = callback

def show(label):
    print(f"\n{label}")
    print(f"GPIO17 (A C1): {counts[17]}")
    print(f"GPIO27 (A C2): {counts[27]}")
    print(f"GPIO22 (B C1): {counts[22]}")
    print(f"GPIO23 (B C2): {counts[23]}")


try:
    show("INITIAL")

    print("\nMotor A running...")
    motor_a.forward(0.25)
    sleep(2)
    motor_a.stop()

    sleep(0.5)
    show("AFTER MOTOR A")

    print("\nMotor B running...")
    motor_b.forward(0.25)
    sleep(2)
    motor_b.stop()

    sleep(0.5)
    show("AFTER MOTOR B")

finally:
    motor_a.stop()
    motor_b.stop()

    motor_a.close()
    motor_b.close()

    for device in pins.values():
      device.close()
