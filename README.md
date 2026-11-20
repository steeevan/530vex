# 530vex

A Python autonomous program for a **VEX IQ (2nd gen)** robot. You pick what to run from a menu on the
robot's brain: the autonomous routine, or a test for each part of the robot.

> **Status:** the speeds, distances and tuning numbers are starting guesses. They have not been tested
> on the real robot yet.

## What it does

- **Drives and turns accurately.** It measures distance with the wheels and direction with the
  brain's built-in inertial sensor. A PID controller slows the robot down as it gets close to where
  it should be.
- **Holds its heading.** While it drives, it keeps correcting so it goes straight.
- **Uses its sensors.** It can back up until the bumper hits a wall, or drive until the distance
  sensor sees something close.
- **Runs the robot's mechanisms.** It can grab and flip with the claw and fire the catapult.
- **Shows a menu on the brain.** You can run the routine or one of the tests, and the screen shows
  how long it took and whether any step ran out of time.

## Files

| File | What it is |
|---|---|
| [`src/main.py`](src/main.py) | The program that downloads to the brain. |
| [`autonomous/main_auto.py`](autonomous/main_auto.py) | A spare copy of the autonomous program. |
| [`tools/sensor_test.py`](tools/sensor_test.py) | A small program that checks the inertial sensor. |
| [`backup/main_driver_original.py`](backup/main_driver_original.py) | The original driver-control program, kept as a backup. |
| [`AUTO_GUIDE.md`](AUTO_GUIDE.md) | The full guide: the menu, writing a routine, and tuning. |

## Robot ports

| Part | Port |
|---|---|
| Left drive motors | 5, 6 |
| Right drive motors (reversed) | 11, 12 |
| Claw / catapult motors (shared) | 4, 10 |
| Pneumatics (cylinder 1 = claw, cylinder 2 = catapult level) | 9 |
| Distance sensor | 3 |
| Bumper (on the back) | 7 |
| Inertial sensor | built into the brain |

If your robot is wired differently, change the ports at the top of `src/main.py`.

## How to run it

1. Install [VS Code](https://code.visualstudio.com/) and the **VEX Robotics** extension.
2. Open this folder in VS Code.
3. Plug in the brain and download the program. It goes to **slot 8** (you can change this in
   `.vscode/vex_project_settings.json`).
4. Put the robot on a flat surface and **don't touch it** while the program starts. The brain
   calibrates its sensor first and shows "HANDS OFF".
5. Use Left/Right to pick a menu item, then press Check to run it.

## Writing a routine

Change the moves in the `routine()` function in `src/main.py`, one move per line:

```python
def routine():
    start_mechanisms()       # open claw, arm catapult (it fires once)
    drive(600, 0)            # forward 600 mm, facing 0 degrees
    claw_cycle()             # grab, flip, release
    turn_to(90)              # turn to face right
    drive(300, 90)           # after a turn, use the NEW heading
    fire_catapult()
    back_until_bumper(90)    # back up until the bumper hits the wall
```

Headings: 0 is the way the robot faces at the start, 90 is right and -90 is left.

The full list of moves and how to tune the numbers are in [AUTO_GUIDE.md](AUTO_GUIDE.md).

## Things to know

- **Keep the program small.** The VEX IQ brain doesn't have much memory. If the program gets too big,
  the brain shows `MemoryError`. The menu shows `mem free` so you can see how much room is left.
- **Don't call `brain_inertial.calibrate()`.** On this robot it never finishes and the sensor gets
  stuck. The brain already calibrates the sensor by itself when the program starts.
