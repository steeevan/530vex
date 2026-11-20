#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

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



# generating and setting random seed
def initializeRandomSeed():
    wait(100, MSEC)
    xaxis = brain_inertial.acceleration(XAXIS) * 1000
    yaxis = brain_inertial.acceleration(YAXIS) * 1000
    zaxis = brain_inertial.acceleration(ZAXIS) * 1000
    systemTime = brain.timer.system() * 100
    urandom.seed(int(xaxis + yaxis + zaxis + systemTime)) 
    
# Initialize random seed 
initializeRandomSeed()

#endregion VEXcode Generated Robot Configuration

# =====================================================================
#  SENSOR TEST PROGRAM (temporary). Tests the brain's inertial sensor.
#  Get the autonomous program back with: git checkout src/main.py
#  Check button = next screen. Errors stay on screen.
# =====================================================================
try:
    import gc
except Exception:
    pass

clock = Timer()


def show(*lines):
    brain.screen.clear_screen()
    brain.screen.set_font(FontType.MONO20)
    row = 1
    for line in lines:
        brain.screen.set_cursor(row, 1)
        brain.screen.print(line[:16])
        row += 1


def show_row(row, text):
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_cursor(row, 1)
    brain.screen.print(("%-16s" % text)[:16])


def wait_release(button):
    while button.pressing():
        wait(20, MSEC)


def wait_for_check():
    wait_release(brain.buttonCheck)
    while not brain.buttonCheck.pressing():
        wait(20, MSEC)
    wait_release(brain.buttonCheck)


def free_memory():
    try:
        gc.collect()
        return gc.mem_free()
    except Exception:
        return -1


def get(function, *args):
    # Ask the sensor for a value. None = the brain refused.
    try:
        return function(*args)
    except Exception:
        return None


def number_text(label, value):
    if value is None:
        return label + " ERROR"
    return "%s %7.2f" % (label, value)


def yes_no(value):
    if value is None:
        return "?"
    if value:
        return "T"
    return "F"


def live(title):
    # Turn the brain by hand and watch which numbers change.
    # rot = rotation, head = heading, rate = spin speed, accZ = gravity (flat = 1)
    # inst = installed, busy = still calibrating   (T = true, F = false)
    show(title + " Check>>")
    wait_release(brain.buttonCheck)
    while not brain.buttonCheck.pressing():
        show_row(2, number_text("rot ", get(brain_inertial.rotation, DEGREES)))
        show_row(3, number_text("head", get(brain_inertial.heading, DEGREES)))
        show_row(4, number_text("rate", get(brain_inertial.gyro_rate, ZAXIS)))
        show_row(5, number_text("accZ", get(brain_inertial.acceleration, ZAXIS)))
        show_row(6, "inst:%s busy:%s" % (
            yes_no(get(brain_inertial.installed)),
            yes_no(get(brain_inertial.is_calibrating))))
        wait(100, MSEC)
    wait_release(brain.buttonCheck)


def find_sensor():
    # Which port numbers 12-31 say "a sensor is here"? (not smart ports 1-12)
    found = ""
    for port in range(12, 32):
        try:
            if Inertial(port).installed():
                found += " " + str(port)
        except Exception:
            pass
    show("TEST 2/4", "default inst: " + yes_no(get(brain_inertial.installed)),
         "ports 12-31 with", "a sensor:", found or "none", "Check: next")
    wait_for_check()


def calibration_test():
    show("TEST 3/4", "Put it flat and", "do not touch.", "", "", "Check: start")
    wait_for_check()
    show("CALIBRATING...", "Do not touch.", "If it stays here", "over 15 seconds,",
         "that IS the", "answer.")
    start = clock.time(MSEC)
    failed = False
    try:
        brain_inertial.calibrate()
    except Exception:
        failed = True
    call_ms = clock.time(MSEC) - start
    busy_after = get(brain_inertial.is_calibrating)
    done_ms = None
    while clock.time(MSEC) - start < 8000:
        if get(brain_inertial.is_calibrating) is False:
            done_ms = clock.time(MSEC) - start
            break
        wait(50, MSEC)
    if failed:
        line2 = "calibrate ERROR"
    else:
        line2 = "took %d ms" % call_ms
    if done_ms is None:
        line4 = "NEVER done (8s)"
    else:
        line4 = "done at %d ms" % done_ms
    show("CAL RESULT", line2, "busy after: " + yes_no(busy_after), line4,
         number_text("rot ", get(brain_inertial.rotation, DEGREES)), "Check: next")
    wait_for_check()


def run_tests():
    show("SENSOR TEST", "mem free:%d" % free_memory(), "Put the robot", "flat. Check: go")
    wait_for_check()
    live("TEST 1/4")
    find_sensor()
    calibration_test()
    live("TEST 4/4")
    show("DONE", "Send me what", "each screen said", "", "", "Check: again")
    wait_for_check()


while True:
    try:
        run_tests()
    except Exception as error:
        text = repr(error)
        show("ERROR", text[0:16], text[16:32], text[32:48], text[48:64], "Check: again")
        wait_for_check()
