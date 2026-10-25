"""Software-only prototype for robot motor commands and encoder speed control.
No Raspberry Pi or GPIO libraries are needed.
"""
from dataclasses import dataclass


def clamp(x, low, high):
    return max(low, min(high, x))


@dataclass
class MockMotor:
    """Representa un motor sin conectarse a ningún dispositivo. Guarda la potencia indicada entre -1 y 1.
    1 = adelante a máxima potencia, -1 = atrás, 0 = parado."""
    power: float = 0.0

    def set_power(self, power):
        self.power = clamp(power, -1.0, 1.0)

    def stop(self):
        self.power = 0.0


class Robot:
    def __init__(self, left, right):
        """coordina ambos motores, con forward para ir alante, speed de 0.4, reverse y turn left, falta turn right"""
        self.left, self.right = left, right

    def drive(self, left_power, right_power):
        self.left.set_power(left_power)
        self.right.set_power(right_power)

    def forward(self, speed=0.4):
        speed = clamp(speed, 0, 1)
        self.drive(speed, speed)

    def reverse(self, speed=0.4):
        speed = clamp(speed, 0, 1)
        self.drive(-speed, -speed)

    def turn_left(self, speed=0.3):
        speed = clamp(speed, 0, 1)
        self.drive(-speed, speed)

    def stop(self):
        self.left.stop()
        self.right.stop()


def encoder_speed(previous_count, current_count, dt, ticks_per_rev):
    """medicion de velocidad, esto si el la formula del lab 7
    Usa la diferencia de pasos y el tiempo transcurrido: rps = (pasos nuevos - pasos anteriores ) / pasos por vuelta * Delta tiempo """
    if dt <= 0 or ticks_per_rev <= 0:
        raise ValueError('dt and ticks_per_rev must be positive')
    return ((current_count - previous_count) / ticks_per_rev) / dt  # revolutions/s


@dataclass
class PIController:
    """Compara continuamente la velocidad que queremos con la velocidad medida. error = objetivo - velocidad_actual
    Si el motor va muy lento, el controlador aumenta la potencia y si va muy rapido al reduce.
    Kp determiina cuanto reacciona el error actual y Ki corrige el error acumulado con el tiempo."""
    kp: float = 0.3
    ki: float = 0.1
    integral: float = 0.0

    def update(self, target_rps, measured_rps, dt):
        if dt <= 0:
            raise ValueError('dt must be positive')
        error = target_rps - measured_rps
        candidate = clamp(self.integral + error * dt, -5.0, 5.0)
        output = self.kp * error + self.ki * candidate
        # Basic anti-windup: don't keep integrating while saturated in the same direction.
        if abs(output) <= 1.0 or (output > 1 and error < 0) or (output < -1 and error > 0):
            self.integral = candidate
        return clamp(self.kp * error + self.ki * self.integral, -1.0, 1.0)


def demo():
    robot = Robot(MockMotor(), MockMotor())
    robot.forward(0.4)
    assert (robot.left.power, robot.right.power) == (0.4, 0.4)
    robot.turn_left(0.3)
    assert (robot.left.power, robot.right.power) == (-0.3, 0.3)
    robot.stop()
    assert (robot.left.power, robot.right.power) == (0, 0)
    assert abs(encoder_speed(100, 140, 0.5, 20) - 4.0) < 1e-9

    controller = PIController(kp=0.6, ki=0.2)
    current_rps = 0.0
    target_rps = 2.0
    dt = 0.1
    print('t(s) target(rps) simulated(rps) command')
    for i in range(60):
        power = controller.update(target_rps, current_rps, dt)
        # Illustrative first-order motor dynamics, NOT a calibrated physical model.
        current_rps += dt * (4.0 * power - current_rps) / 0.5
        if i % 10 == 0 or i == 59:
            print(f'{(i+1)*dt:4.1f}  {target_rps:6.2f}       {current_rps:6.2f}     {power:6.2f}')
    print('PASS: movement commands, stop, encoder formula, software simulation')


if __name__ == '__main__':
    demo()
