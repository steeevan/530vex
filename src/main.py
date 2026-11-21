#region VEXcode Generated Robot Configuration
from vex import *

# Brain should be defined by default
brain=Brain()

# Robot configuration code
brain_inertial = Inertial()
controller = Controller()
L_motor_a = Motor(Ports.PORT5, False)
L_motor_b = Motor(Ports.PORT6, False)
L = MotorGroup(L_motor_a, L_motor_b)
R_motor_a = Motor(Ports.PORT11, True)
R_motor_b = Motor(Ports.PORT12, True)
R = MotorGroup(R_motor_a, R_motor_b)
C_L = Motor(Ports.PORT4, False)
C_R = Motor(Ports.PORT10, True)
pneumatic_9 = Pneumatic(Ports.PORT9)
distance_3 = Distance(Ports.PORT3)
Bumper_1 = Bumper(Ports.PORT7)

#endregion VEXcode Generated Robot Configuration

# =====================================================================
#  AUTONOMOUS PROGRAM (VEX IQ 2nd gen).  Help: docs/robot-guide.md
#  Lessons that explain every function: docs/lessons/
#  NO MENU: start the program and routine() runs right away.
#  Edit only: SETTINGS (numbers) and routine() (the moves).
#  Old driver program: programs/driver_original.py (and brain slot 4).
#  Sensor test program: programs/sensor_test.py (copy it into src/main.py).
#  START THE PROGRAM WITH THE ROBOT STILL (the sensor calibrates at start).
#  KEEP THIS FILE SMALL - the brain gives MemoryError if it gets too big.
# =====================================================================
try:
    import gc
except Exception:
    pass

# ---------------------------------------------------------------------
#  SETTINGS - ALL UNTESTED STARTING GUESSES. Speed = %, distance = mm.
# ---------------------------------------------------------------------
# mm moved per degree of wheel turn (guess: 200 mm per turn / 360).
# FIX: make routine() only drive(500, 0). If it really goes D mm:
#      new MM_PER_DEGREE = old MM_PER_DEGREE * D / 500
MM_PER_DEGREE = 0.556
# 1 or -1. Turn the robot CLOCKWISE by hand (programs/sensor_test.py
# shows it): rot must go UP. If it goes down, use -1.
HEADING_DIRECTION = 1

LOOP_MS = 20             # control loop time
ACCEL_STEP = 4           # most speed can rise per loop (lower = less slip)
SETTLE_MS = 120          # stay inside tolerance this long = done

TURN_KP = 0.9            # % per degree of error (higher = turns harder)
TURN_KI = 0.0            # 0 unless it always stops a bit short
TURN_KD = 0.06           # higher = less overshoot
TURN_I_ZONE = 10         # degrees (I only works this close)
TURN_MAX_SPEED = 50
TURN_MIN_SPEED = 6       # so it never stalls near the end
TURN_TOLERANCE = 1.0     # degrees
TURN_TIMEOUT_MS = 3000

DRIVE_KP = 0.4           # % per mm of error (higher = brakes later)
DRIVE_KI = 0.0
DRIVE_KD = 0.02          # higher = softer stop
DRIVE_I_ZONE = 30        # mm
DRIVE_MAX_SPEED = 60
DRIVE_MIN_SPEED = 8
DRIVE_TOLERANCE = 5      # mm
DRIVE_TIME_BASE_MS = 1500    # drive time limit = BASE + mm * PER_MM
DRIVE_TIME_PER_MM = 8

HEADING_KP = 1.5         # drift fix, % per degree (higher = fixes harder)
HEADING_KI = 0.0
HEADING_KD = 0.0
HEADING_I_ZONE = 5
HEADING_MAX_CORRECTION = 20  # %

BUMPER_SPEED = 20        # slow, to hit the wall gently
BUMPER_TIMEOUT_MS = 4000
SENSOR_SPEED = 30
SENSOR_TIMEOUT_MS = 4000

INERTIAL_WAIT_MS = 8000     # most it waits for the sensor at program start

# Mechanism timings, copied from the driver program (only change if the
# mechanism changed). The two TIMEOUTs are new.
CATAPULT_RELEASE_MS = 250
CATAPULT_WIND_MS = 700
CATAPULT_STOPPED_BELOW = 5
CATAPULT_STALL_TIMEOUT_MS = 2000
CLAW_GRIP_MS = 200
CLAW_ARM_DEGREES = 145
CLAW_ARM_TIMEOUT_MS = 2000
CLAW_RELEASE_MS = 50
CLAW_RETURN_SPEED = 75
CLAW_RETURN_MS = 500


# ---------------------------------------------------------------------
#  YOUR ROUTINE - it runs as soon as the program starts.
#   start_mechanisms()   open claw, catapult Level 4 (does NOT fire)
#   drive(mm, heading)   negative mm = backward
#   turn_to(heading)     spin in place
#   drive(mm, heading, 100) / turn_to(heading, 100): last number = top speed
#   back_until_bumper(heading)
#   drive_until_distance(mm, heading, speed)   speed +/- = direction
#   set_heading(value)   say "I am facing value now"
#   claw_open() claw_close() claw_cycle()      cycle = grab, flip, release
#   fire_catapult()   set_catapult_level(3 or 4)   wait(500, MSEC)
#  Headings: 0 = the way the robot faced at start, 90 = right, -90 = left.
# ---------------------------------------------------------------------
def routine():
    start_mechanisms()       # open claw, Level 4 (catapult must be armed)
    # shoot the preload
    drive(-50, 0, 100)       # back 50 mm, facing 0 degrees, top speed 100
    turn_to(-32)             # turn a little left
    drive(-150, -32, 100)
    fire_catapult()

    # grab first yellow
    drive(80, -32, 100)
    turn_to(-190)
    drive(130, -190, 100)
    claw_cycle()

    # shoot first yellow
    drive(-130, -190, 100)
    turn_to(-35)
    drive(-100, -35, 100)
    fire_catapult()

    # grab second yellow
    drive(100, -35, 100)
    turn_to(203)
    drive(140, 203, 100)
    turn_to(190, 100)
    drive(20, 190, 100)
    claw_cycle()

    # shoot second yellow
    drive(-155, 190)
    turn_to(-39, 100)
    drive(-150, -39, 100)
    fire_catapult()

    #---40 seconds---
    # red
    drive(80, -35, 100)
    turn_to(60, 100)
    drive(200, 60, 100)
    claw_cycle()

    turn_to(92, 100)
    drive(-200, 92, 100)
    drive(-100, 90, 100)
    set_catapult_level(3)
    fire_catapult()

    #back_until_bumper(90)   # square up on the wall
    # set_heading(90)        # optional: after squaring, say "I am at 90"
    set_catapult_level(3)


# =====================================================================
#  DON'T EDIT BELOW THIS LINE
# =====================================================================

# ---------------------------------------------------------------------
#  Helpers: time, angles, PID, settling (lessons 2, 3 and 4)
# ---------------------------------------------------------------------
clock = Timer()
problem_count = 0        # moves that ran out of time
last_problem = ""


def now_ms():
    return clock.time(MSEC)


def clamp(value, low, high):
    return min(max(value, low), high)


def angle_diff(target, current):
    # Turn needed (clockwise = +), always the short way: -180..+180
    diff = (target - current) % 360
    if diff > 180:
        diff -= 360
    return diff


def heading_now():
    # rotation() has no 359 -> 0 jump
    return brain_inertial.rotation(DEGREES) * HEADING_DIRECTION


def set_heading(value):
    brain_inertial.set_rotation(value * HEADING_DIRECTION, DEGREES)


def report_problem(name):
    global problem_count, last_problem
    problem_count += 1
    last_problem = name


def free_memory():
    try:
        gc.collect()
        return gc.mem_free()
    except Exception:
        return -1


class PID:
    # error in -> power out. P = push by the error, I = fix a small
    # leftover (only inside i_zone), D = brake as the error shrinks.
    def __init__(self, kp, ki, kd, i_zone):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_zone = i_zone
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None

    def update(self, error):
        now = now_ms()
        output = self.kp * error
        if self.last_time is not None:
            seconds = (now - self.last_time) / 1000.0
            if seconds > 0:
                if self.ki != 0 and abs(error) < self.i_zone:
                    self.integral += error * seconds
                else:
                    self.integral = 0.0
                output += self.kd * (error - self.last_error) / seconds
        output += self.ki * self.integral
        self.last_error = error
        self.last_time = now
        return output


class Settle:
    # True once the error has stayed inside the tolerance long enough.
    def __init__(self, tolerance, settle_ms):
        self.tolerance = tolerance
        self.settle_ms = settle_ms
        self.since = None
        self.inside = False

    def update(self, error):
        self.inside = abs(error) <= self.tolerance
        if not self.inside:
            self.since = None
            return False
        if self.since is None:
            self.since = now_ms()
        return now_ms() - self.since >= self.settle_ms


def ramp(current, target, step):
    # Slowing down is instant. Speeding up / reversing is limited to step.
    if abs(target) <= abs(current) and target * current >= 0:
        return target
    if target > current + step:
        return current + step
    if target < current - step:
        return current - step
    return target


def keep_moving(speed, min_speed, error):
    # Too little power to move? Use min_speed.
    if abs(speed) < min_speed:
        if error > 0:
            return min_speed
        return -min_speed
    return speed


# ---------------------------------------------------------------------
#  Drive base (lesson 5). Each move returns True (arrived) or False
#  (ran out of time) and always brakes at the end.
# ---------------------------------------------------------------------
def setup_motors():
    L.set_stopping(BRAKE)
    R.set_stopping(BRAKE)
    L.set_max_torque(100, PERCENT)
    R.set_max_torque(100, PERCENT)
    C_L.set_max_torque(100, PERCENT)
    C_R.set_max_torque(100, PERCENT)


def drive_motors(left, right):
    # Left faster than right = turns clockwise.
    L.spin(FORWARD, clamp(left, -100, 100), PERCENT)
    R.spin(FORWARD, clamp(right, -100, 100), PERCENT)


def brake_drive():
    L.stop(BRAKE)
    R.stop(BRAKE)


def wheel_degrees():
    return (L.position(DEGREES) + R.position(DEGREES)) / 2.0


def heading_correction(pid, target_heading):
    error = angle_diff(target_heading, heading_now())
    return clamp(pid.update(error), -HEADING_MAX_CORRECTION, HEADING_MAX_CORRECTION)


def turn_to(heading, max_speed=TURN_MAX_SPEED):
    pid = PID(TURN_KP, TURN_KI, TURN_KD, TURN_I_ZONE)
    settle = Settle(TURN_TOLERANCE, SETTLE_MS)
    start_time = now_ms()
    speed = 0
    done = False
    while now_ms() - start_time < TURN_TIMEOUT_MS:
        error = angle_diff(heading, heading_now())
        wanted = pid.update(error)
        if settle.update(error):
            done = True
            break
        if settle.inside:
            wanted = 0
        else:
            wanted = clamp(wanted, -max_speed, max_speed)
            wanted = keep_moving(wanted, TURN_MIN_SPEED, error)
        speed = ramp(speed, wanted, ACCEL_STEP)
        drive_motors(speed, -speed)
        wait(LOOP_MS, MSEC)
    brake_drive()
    if not done:
        report_problem("turn")
    return done


def drive(distance_mm, heading, max_speed=DRIVE_MAX_SPEED):
    distance_pid = PID(DRIVE_KP, DRIVE_KI, DRIVE_KD, DRIVE_I_ZONE)
    heading_pid = PID(HEADING_KP, HEADING_KI, HEADING_KD, HEADING_I_ZONE)
    settle = Settle(DRIVE_TOLERANCE, SETTLE_MS)
    start_degrees = wheel_degrees()
    time_limit = DRIVE_TIME_BASE_MS + abs(distance_mm) * DRIVE_TIME_PER_MM
    start_time = now_ms()
    speed = 0
    done = False
    while now_ms() - start_time < time_limit:
        moved_mm = (wheel_degrees() - start_degrees) * MM_PER_DEGREE
        error = distance_mm - moved_mm
        wanted = distance_pid.update(error)
        turn = heading_correction(heading_pid, heading)
        if settle.update(error):
            done = True
            break
        if settle.inside:
            wanted = 0
            turn = 0
        else:
            wanted = clamp(wanted, -max_speed, max_speed)
            wanted = keep_moving(wanted, DRIVE_MIN_SPEED, error)
        speed = ramp(speed, wanted, ACCEL_STEP)
        drive_motors(speed + turn, speed - turn)
        wait(LOOP_MS, MSEC)
    brake_drive()
    if not done:
        report_problem("drive")
    return done


# ---------------------------------------------------------------------
#  Moves that stop when a sensor says so (lesson 6)
# ---------------------------------------------------------------------
def back_until_bumper(heading, speed=BUMPER_SPEED):
    heading_pid = PID(HEADING_KP, HEADING_KI, HEADING_KD, HEADING_I_ZONE)
    start_time = now_ms()
    current = 0
    done = False
    while now_ms() - start_time < BUMPER_TIMEOUT_MS:
        if Bumper_1.pressing():
            done = True
            break
        turn = heading_correction(heading_pid, heading)
        current = ramp(current, -abs(speed), ACCEL_STEP)
        drive_motors(current + turn, current - turn)
        wait(LOOP_MS, MSEC)
    brake_drive()
    if not done:
        report_problem("bumper")
    return done


def drive_until_distance(mm, heading, speed=SENSOR_SPEED):
    # Sign of speed = direction (we don't know which way the sensor points).
    heading_pid = PID(HEADING_KP, HEADING_KI, HEADING_KD, HEADING_I_ZONE)
    start_time = now_ms()
    current = 0
    close_count = 0
    done = False
    while now_ms() - start_time < SENSOR_TIMEOUT_MS:
        close = False
        if distance_3.is_object_detected():
            close = distance_3.object_distance(MM) <= mm
        if close:
            close_count += 1
        else:
            close_count = 0
        if close_count >= 2:         # 2 readings in a row = not a glitch
            done = True
            break
        turn = heading_correction(heading_pid, heading)
        current = ramp(current, speed, ACCEL_STEP)
        drive_motors(current + turn, current - turn)
        wait(LOOP_MS, MSEC)
    brake_drive()
    if not done:
        report_problem("sensor")
    return done


# ---------------------------------------------------------------------
#  Mechanisms (lesson 7). C_L and C_R share two jobs: same sign = claw arm,
#  opposite signs = catapult. Moves and timings copied from the driver.
# ---------------------------------------------------------------------
def mechanism_spin(left, right):
    C_L.set_velocity(left, PERCENT)
    C_R.set_velocity(right, PERCENT)
    C_L.spin(FORWARD)
    C_R.spin(FORWARD)


def mechanism_stop(mode):
    C_L.set_stopping(mode)
    C_R.set_stopping(mode)
    C_L.stop()
    C_R.stop()


def claw_open():
    pneumatic_9.retract(CYLINDER1)


def claw_close():
    pneumatic_9.extend(CYLINDER1)
    wait(CLAW_GRIP_MS, MSEC)


def set_catapult_level(level):
    # Level 3 = cylinder 2 retracted, Level 4 = extended.
    if level == 3:
        pneumatic_9.retract(CYLINDER2)
    elif level == 4:
        pneumatic_9.extend(CYLINDER2)


def start_mechanisms():
    # Open the claw and pick Level 4. It does NOT fire the catapult, so
    # arm the catapult and load the preload BEFORE starting the program.
    # (No pump_on(): the driver never calls it. If the cylinders don't
    # move, add pneumatic_9.pump_on() here.)
    claw_open()
    set_catapult_level(4)


def fire_catapult():
    # Short spin releases it, second spin winds it down until it stalls.
    mechanism_spin(-100, 100)
    wait(CATAPULT_RELEASE_MS, MSEC)
    mechanism_spin(100, -100)
    wait(CATAPULT_WIND_MS, MSEC)
    start_time = now_ms()
    done = True
    while abs(C_R.velocity(PERCENT)) >= CATAPULT_STOPPED_BELOW:
        if now_ms() - start_time > CATAPULT_STALL_TIMEOUT_MS:
            done = False
            break
        wait(20, MSEC)
    mechanism_stop(BRAKE)
    if not done:
        report_problem("catapult")
    return done


def claw_cycle():
    # Grab, swing the arm over, let go, swing back.
    claw_close()
    C_L.set_stopping(BRAKE)
    C_R.set_stopping(BRAKE)
    mechanism_spin(-100, -100)
    C_L.set_position(0, DEGREES)
    start_time = now_ms()
    done = True
    while abs(C_L.position(DEGREES)) <= CLAW_ARM_DEGREES:
        if now_ms() - start_time > CLAW_ARM_TIMEOUT_MS:
            done = False
            break
        wait(20, MSEC)
    claw_open()
    wait(CLAW_RELEASE_MS, MSEC)
    mechanism_spin(CLAW_RETURN_SPEED, CLAW_RETURN_SPEED)
    wait(CLAW_RETURN_MS, MSEC)
    mechanism_stop(COAST)
    if not done:
        report_problem("claw arm")
    return done


# ---------------------------------------------------------------------
#  Brain screen (lesson 8): 6 rows x 16 letters (MONO20 font)
# ---------------------------------------------------------------------
def show(*lines):
    brain.screen.clear_screen()
    brain.screen.set_font(FontType.MONO20)
    row = 1
    for line in lines:
        brain.screen.set_cursor(row, 1)
        brain.screen.print(line[:16])
        row += 1


def wait_release(button):
    while button.pressing():
        wait(20, MSEC)


def wait_for_check():
    wait_release(brain.buttonCheck)
    while not brain.buttonCheck.pressing():
        wait(20, MSEC)
    wait_release(brain.buttonCheck)


def show_result(seconds):
    # The screen after the routine: time, heading, and any timeouts.
    if problem_count == 0:
        status1 = "All steps OK"
        status2 = ""
    else:
        status1 = "%d TIMEOUT(S)" % problem_count
        status2 = "last: " + last_problem
    show("ROUTINE DONE", "Time %.1f s" % seconds, "Heading %.1f" % heading_now(),
         status1, status2, "mem free:%d" % free_memory())


def show_error(error):
    # Stop the robot and show the error ON THE BRAIN SCREEN, so you can
    # read it without the console. Write down what it says.
    try:
        brake_drive()
        mechanism_stop(BRAKE)
    except Exception:
        pass
    text = repr(error)
    show("ERROR", text[0:16], text[16:32], text[32:48], text[48:64],
         "mem free:%d" % free_memory())


def wait_for_inertial():
    # The brain calibrates the inertial sensor BY ITSELF when the program
    # starts (the robot must be STILL). We only wait for it to finish.
    # Do not call brain_inertial.calibrate(): on this robot it never ends.
    show("HANDS OFF!", "Inertial sensor", "starting up.", "Do not touch.")
    start_time = now_ms()
    while brain_inertial.is_calibrating():
        if now_ms() - start_time > INERTIAL_WAIT_MS:
            show("INERTIAL BUSY", "Stop the program", "and start it", "again. Keep the",
                 "robot still.", "Check: go on")
            wait_for_check()
            return
        wait(50, MSEC)


# ---------------------------------------------------------------------
#  Start (lesson 1). No menu: the routine runs as soon as the program
#  starts. If anything crashes, the error is shown on the brain screen.
# ---------------------------------------------------------------------
def run_routine():
    setup_motors()
    wait_for_inertial()
    brain_inertial.set_rotation(0, DEGREES)    # 0 = the way the robot faces now
    show("RUNNING")
    start_time = now_ms()
    routine()
    show_result((now_ms() - start_time) / 1000.0)


try:
    run_routine()
except Exception as error:
    show_error(error)

while True:              # keep the last screen up until you press X
    wait(100, MSEC)
