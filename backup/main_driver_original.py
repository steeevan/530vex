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

screen_precision = 0
console_precision = 0
deadBand = 0
X = 0
Y = 0
jia_zi = 0
fan_zhuan = 0
fan_zhuan_jiao_du = 0
JIAZI = 0
yaokong = 0
k = 0
tan_she = 0
Level = 0
message1 = Event()
joystick = Event()
tan_she_xia_ya = Event()

def Differential_L_Differential_L_Differential_R_Differential_R(Differential_L_Differential_L_Differential_R_Differential_R__Differential_L, Differential_L_Differential_L_Differential_R_Differential_R__Differential_R):
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    C_L.set_velocity(Differential_L_Differential_L_Differential_R_Differential_R__Differential_L, PERCENT)
    C_R.set_velocity(Differential_L_Differential_L_Differential_R_Differential_R__Differential_R, PERCENT)
    C_L.spin(FORWARD)
    C_R.spin(FORWARD)

def joystick_callback_0():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    # Base
    deadBand = 15
    L.set_stopping(BRAKE)
    R.set_stopping(BRAKE)
    L.set_max_torque(100, PERCENT)
    R.set_max_torque(100, PERCENT)
    while True:
        if yaokong == 0:
            # Joystick movement
            X = controller.axisC.position()
            Y = controller.axisA.position()
            if math.fabs(Y) + math.fabs(X) > deadBand:
                X = X * 0.6
                Y = Y * 1.1
                L.set_velocity((k * Y + X), PERCENT)
                R.set_velocity((k * Y - X), PERCENT)
                L.spin(FORWARD)
                R.spin(FORWARD)
            else:
                L.stop()
                R.stop()
        wait(20, MSEC)

def message1_callback_0():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    # Catapult mechanism
    C_L.set_max_torque(100, PERCENT)
    C_R.set_max_torque(100, PERCENT)
    tan_she_xia_ya.broadcast_and_wait()
    Level = 3
    pneumatic_9.retract(CYLINDER2)
    while True:
        if controller.buttonLUp.pressing():
            if Level == 3:
                tan_she_xia_ya.broadcast()
            else:
                Level = 3
                pneumatic_9.retract(CYLINDER2)
            while not not controller.buttonLUp.pressing():
                wait(20, MSEC)
        if controller.buttonLDown.pressing():
            if Level == 4:
                tan_she_xia_ya.broadcast()
            else:
                Level = 4
                pneumatic_9.extend(CYLINDER2)
            while not not controller.buttonLDown.pressing():
                wait(20, MSEC)
        wait(20, MSEC)

def tan_she_xia_ya_callback_0():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    tan_she = 1
    Differential_L_Differential_L_Differential_R_Differential_R(-100, 100)
    wait(0.25, SECONDS)
    Differential_L_Differential_L_Differential_R_Differential_R(100, -100)
    wait(0.7, SECONDS)
    while not math.fabs(C_R.velocity(PERCENT)) < 5:
        wait(20, MSEC)
    C_L.set_stopping(BRAKE)
    C_R.set_stopping(BRAKE)
    C_L.stop()
    C_R.stop()
    tan_she = 0

def message1_callback_1():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    # Claw
    jia_zi = 0
    pneumatic_9.retract(CYLINDER1)
    while True:
        if controller.buttonRUp.pressing():
            jia_zi = 1
            pneumatic_9.extend(CYLINDER1)
            wait(0.2, SECONDS)
            while not tan_she == 0:
                wait(20, MSEC)
            C_L.set_stopping(BRAKE)
            C_R.set_stopping(BRAKE)
            Differential_L_Differential_L_Differential_R_Differential_R(-100, -100)
            C_L.set_position(0, DEGREES)
            while not math.fabs(C_L.position(DEGREES)) > 145:
                wait(20, MSEC)
            pneumatic_9.retract(CYLINDER1)
            wait(0.05, SECONDS)
            Differential_L_Differential_L_Differential_R_Differential_R(75, 75)
            wait(0.5, SECONDS)
            C_L.set_stopping(COAST)
            C_R.set_stopping(COAST)
            C_L.stop()
            C_R.stop()
        wait(20, MSEC)

def when_started1():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    joystick.broadcast()
    message1.broadcast()

def when_started2():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    while True:
        screen_precision = 0
        screen_precision = 1
        brain.screen.set_font(FontType.PROP60)
        brain.screen.set_cursor(1, 1)
        brain.screen.print(distance_3.object_distance(MM), precision=screen_precision)
        wait(20, MSEC)

def joystick_callback_1():
    global deadBand, X, Y, jia_zi, fan_zhuan, fan_zhuan_jiao_du, JIAZI, yaokong, k, tan_she, Level, message1, joystick, _E6_B6_88_E6_81_AF1, encourage, Pneumatic_1, Pneumatic_2, fang_ka_si, power_take_off, _E6_88_91_E7_9A_84_E4_BA_8B_E4_BB_B6, tan_she_xia_ya, screen_precision, console_precision
    k = 1
    while True:
        while not (Bumper_1.pressing() and Y < -20):
            wait(20, MSEC)
        k = 0.2
        wait(0.1, SECONDS)
        k = 0.25
        while not Y > 20:
            wait(20, MSEC)
        k = 1
        wait(20, MSEC)

# system event handlers
joystick(joystick_callback_0)
joystick(joystick_callback_1)
message1(message1_callback_0)
message1(message1_callback_1)
tan_she_xia_ya(tan_she_xia_ya_callback_0)
# add 15ms delay to make sure events are registered correctly.
wait(15, MSEC)

ws2 = Thread( when_started2 )
when_started1()
