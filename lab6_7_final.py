
"""Labs 6 and 7: rover control and speed simulation.

No Raspberry Pi is required.
Run with --test, --demo or --keyboard.
"""

import argparse
import csv
from dataclasses import dataclass, field


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def encoder_speed(previous_count, current_count, dt, ticks_per_rev):
    """Calculate signed wheel speed in revolutions per second."""
    if dt <= 0 or ticks_per_rev <= 0:
        raise ValueError("Time and ticks_per_rev must be positive")

    return (current_count - previous_count) / (ticks_per_rev * dt)


@dataclass
class MockMotor:
    """Simulated motor receiving a normalized power command."""
    power: float = 0.0

    def set_power(self, value):
        self.power = clamp(value, -1.0, 1.0)

    def stop(self):
        self.power = 0.0


class Robot:
    """Coordinate the movement of two motors."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def drive(self, left_power, right_power):
        self.left.set_power(left_power)
        self.right.set_power(right_power)

    def forward(self, speed=0.4):
        speed = clamp(speed, 0, 1)
        self.drive(speed, speed)

    def backward(self, speed=0.4):
        speed = clamp(speed, 0, 1)
        self.drive(-speed, -speed)

    def left_turn(self, speed=0.3):
        speed = clamp(speed, 0, 1)
        self.drive(-speed, speed)

    def right_turn(self, speed=0.3):
        speed = clamp(speed, 0, 1)
        self.drive(speed, -speed)

    def stop(self):
        self.left.stop()
        self.right.stop()


@dataclass
class PIController:
    """Proportional-integral speed controller."""
    kp: float = 0.3
    ki: float = 0.1
    integral: float = 0.0

    def reset(self):
        self.integral = 0.0

    def update(self, target_rps, measured_rps, dt):
        if dt <= 0:
            raise ValueError("dt must be positive")

        error = target_rps - measured_rps

        candidate = clamp(
            self.integral + error * dt, -5.0, 5.0
        )

        raw = self.kp * error + self.ki * candidate

        # Basic anti-windup protection
        if (abs(raw) <= 1.0
                or (raw > 1 and error < 0)
                or (raw < -1 and error > 0)):
            self.integral = candidate

        command = (
            self.kp * error + self.ki * self.integral
        )

        return clamp(command, -1.0, 1.0)


@dataclass
class VirtualWheel:
    """Simulate wheel dynamics and encoder ticks."""
    gain_rps: float = 4.0
    time_constant: float = 0.5
    ticks_per_rev: int = 200
    velocity_rps: float = 0.0
    encoder_count: int = 0
    fractional_ticks: float = field(default=0.0, repr=False)

    def step(self, power, dt):
        if dt <= 0 or self.time_constant <= 0:
            raise ValueError("Invalid simulation parameters")

        # Simplified first-order motor model
        acceleration = (
            self.gain_rps * power - self.velocity_rps
        ) / self.time_constant

        self.velocity_rps += acceleration * dt

        # Convert wheel movement to simulated encoder ticks
        tick_change = (
            self.fractional_ticks
            + self.velocity_rps * dt * self.ticks_per_rev
        )

        whole_ticks = int(tick_change)
        self.fractional_ticks = tick_change - whole_ticks
        self.encoder_count += whole_ticks


class RoverSimulation:
    """Connect two motors, encoders and PI controllers."""

    def __init__(self, kp=0.3, ki=0.1, dt=0.1):
        self.robot = Robot(MockMotor(), MockMotor())

        # Different wheel gains simulate unequal motors
        self.left_wheel = VirtualWheel(gain_rps=4.0)
        self.right_wheel = VirtualWheel(gain_rps=3.6)

        self.left_pi = PIController(kp, ki)
        self.right_pi = PIController(kp, ki)

        self.dt = dt
        self.time = 0.0

        self.target_left = 0.0
        self.target_right = 0.0

        self.last_left_speed = 0.0
        self.last_right_speed = 0.0

        self.rows = []

    def set_targets(self, left_rps, right_rps):
        new_targets = (left_rps, right_rps)
        old_targets = (self.target_left, self.target_right)

        if new_targets != old_targets:
            self.left_pi.reset()
            self.right_pi.reset()

        self.target_left = left_rps
        self.target_right = right_rps

    def command(self, key):
        """Translate keyboard commands into wheel speed targets."""
        commands = {
            "w": (2.0, 2.0),
            "s": (-2.0, -2.0),
            "a": (-1.0, 1.0),
            "d": (1.0, -1.0),
            "e": (0.0, 0.0),
            "q": (0.0, 0.0),
        }

        key = key.lower().strip()

        if key not in commands:
            raise ValueError("Use W, A, S, D, E or Q")

        self.set_targets(*commands[key])

    def step(self):
        """Execute one closed-loop control step."""
        dt = self.dt

        left_before = self.left_wheel.encoder_count
        right_before = self.right_wheel.encoder_count

        # Controllers use encoder-derived speeds
        left_power = self.left_pi.update(
            self.target_left, self.last_left_speed, dt
        )

        right_power = self.right_pi.update(
            self.target_right, self.last_right_speed, dt
        )

        # Stop applying power when a target is zero
        if self.target_left == 0:
            left_power = 0.0
            self.left_pi.reset()

        if self.target_right == 0:
            right_power = 0.0
            self.right_pi.reset()

        self.robot.drive(left_power, right_power)

        # Move virtual wheels
        self.left_wheel.step(self.robot.left.power, dt)
        self.right_wheel.step(self.robot.right.power, dt)

        # Read the simulated encoders
        self.last_left_speed = encoder_speed(
            left_before,
            self.left_wheel.encoder_count,
            dt,
            self.left_wheel.ticks_per_rev
        )

        self.last_right_speed = encoder_speed(
            right_before,
            self.right_wheel.encoder_count,
            dt,
            self.right_wheel.ticks_per_rev
        )

        self.time += dt

        result = {
            "time_s": round(self.time, 3),
            "target_left_rps": self.target_left,
            "measured_left_rps": self.last_left_speed,
            "left_power": left_power,
            "target_right_rps": self.target_right,
            "measured_right_rps": self.last_right_speed,
            "right_power": right_power,
            "left_encoder_ticks": self.left_wheel.encoder_count,
            "right_encoder_ticks": self.right_wheel.encoder_count
        }

        self.rows.append(result)
        return result

    def run(self, seconds):
        steps = round(seconds / self.dt)
        return [self.step() for _ in range(steps)]

    def save_csv(self, filename):
        if not self.rows:
            return

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=list(self.rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(self.rows)


def show(result):
    print(
        f"{result['time_s']:5.1f}s | "
        f"LEFT: target={result['target_left_rps']:+.1f}, "
        f"speed={result['measured_left_rps']:+.2f}, "
        f"power={result['left_power']:+.2f} | "
        f"RIGHT: target={result['target_right_rps']:+.1f}, "
        f"speed={result['measured_right_rps']:+.2f}, "
        f"power={result['right_power']:+.2f}"
    )


def self_test():
    """Test commands, encoder calculations and feedback."""
    robot = Robot(MockMotor(), MockMotor())

    tests = [
        (robot.forward, (0.4, 0.4)),
        (robot.backward, (-0.4, -0.4)),
        (robot.left_turn, (-0.3, 0.3)),
        (robot.right_turn, (0.3, -0.3)),
        (robot.stop, (0.0, 0.0))
    ]

    for action, expected in tests:
        action()
        actual = (robot.left.power, robot.right.power)
        assert actual == expected

    assert encoder_speed(100, 140, 0.5, 20) == 4.0
    assert encoder_speed(140, 100, 0.5, 20) == -4.0

    sim = RoverSimulation()
    assert sim.left_pi is not sim.right_pi

    sim.command("w")
    sim.run(6)
    assert sim.last_left_speed > 1
    assert sim.last_right_speed > 1

    sim.command("a")
    sim.run(3)
    assert sim.last_left_speed < 0 < sim.last_right_speed

    sim.command("d")
    sim.run(3)
    assert sim.last_left_speed > 0 > sim.last_right_speed

    sim.command("s")
    sim.run(3)
    assert sim.last_left_speed < 0
    assert sim.last_right_speed < 0

    sim.command("e")
    sim.run(3)
    assert abs(sim.last_left_speed) < 0.1
    assert abs(sim.last_right_speed) < 0.1

    print("PASS: movement, stop, encoders and two-wheel PI")


def demo():
    """Run automatic movement experiments."""
    sim = RoverSimulation()

    experiments = [
        ("w", 6),
        ("a", 3),
        ("d", 3),
        ("s", 3),
        ("e", 3)
    ]

    for key, duration in experiments:
        sim.command(key)
        sim.run(duration)

        print(f"\nCommand {key.upper()}:")
        show(sim.rows[-1])

    sim.save_csv("iot_lab6_7_results.csv")
    print("\nCSV saved: iot_lab6_7_results.csv")


def keyboard():
    """Interactive command mode; press Enter after each key."""
    sim = RoverSimulation()

    print("W=Forward, S=Backward, A=Left")
    print("D=Right, E=Stop, Q=Quit")
    print("Each command simulates 2 seconds.")

    try:
        while True:
            key = input("Command: ").lower().strip()

            if key not in ("w", "a", "s", "d", "e", "q"):
                print("Invalid command")
                continue

            sim.command(key)

            if key == "q":
                break

            result = sim.run(2)[-1]
            show(result)

    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted")

    finally:
        sim.command("e")
        sim.robot.stop()
        sim.save_csv("iot_lab6_7_keyboard_results.csv")
        print("Simulation stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--test", action="store_true")
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--keyboard", action="store_true")

    args = parser.parse_args()

    if args.test:
        self_test()
    elif args.demo:
        demo()
    elif args.keyboard:
        keyboard()
