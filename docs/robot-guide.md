# Autonomous program guide

None of the numbers in the program have been tested on the real robot yet. They are starting guesses.

To learn how the program works inside (the math and the reasons behind it), see the [lessons](README.md).

## Which file is which

| File | What it is |
|---|---|
| `src/main.py` | The ONLY file that downloads to the brain. It holds the autonomous program. |
| `programs/sensor_test.py` | A small program that tests the brain's inertial sensor. |
| `programs/driver_original.py` | The old driver-control program (also in brain slot 4). |

To run one of the other programs: copy its text into `src/main.py`, then download to slot 8.
Never download over slot 4.

To get the autonomous program back afterwards, run `git checkout src/main.py` in the VS Code
terminal, or copy `src/main.py` from GitHub.

**Keep the program small.** The brain has little memory. If the program gets too big the brain
shows `MemoryError`. Long comments and extra features both use memory.
The menu shows `mem free` so you can see how much room is left.

## The brain menu

Left/Right = pick an item. Check = run it.

**Start the program with the robot STILL.** The brain calibrates its inertial sensor by itself when
the program starts, and the screen says HANDS OFF until it is done. Each time you press Check, the
heading is set to 0 (= the way the robot faces right then).

Do not add `brain_inertial.calibrate()` to the program. On this robot it never finishes
and leaves the sensor stuck.

| Item | What it does |
|---|---|
| Routine | Runs `routine()`. |
| Show heading | Shows the heading. Turn the robot clockwise by hand: the number must go UP. If it goes down, set `HEADING_DIRECTION = -1`. |
| Turn test | Four 90 degree turns, then shows the error. |
| Drive test | Drives 500 mm. Measure the real distance D, then `MM_PER_DEGREE = old * D / 500`. |
| Catapult / Claw | Test each mechanism alone. |

If a crash happens, the error stays on the brain screen until you press Check.

## Headings

0 = the way the robot faced at the start. 90 = turned right. -90 = turned left.
Every move names the heading it wants, so small mistakes do not add up.

## Writing a routine

Edit `routine()` only. One move per line:

- `drive(600, 0)` forward 600 mm, facing 0. A negative number goes backward.
- `turn_to(90)` spin in place to face 90.
- `claw_cycle()` grab, flip, release.
- `fire_catapult()` fire and wind back.
- `back_until_bumper(90)` reverse slowly until the back bumper hits the wall.
- `drive_until_distance(mm, heading, speed)` drive until the distance sensor reads `mm` or less. `speed` + or - picks the direction.
- `set_heading(90)` after squaring on a wall, say "I am facing 90 now".
- `wait(500, MSEC)` pause half a second.

`start_mechanisms()` arms the catapult and it FIRES once. Load no game piece before it.
To start WITHOUT firing, use these two lines instead (arm the catapult by hand first):
`claw_open()` and `set_catapult_level(3)`. Fire later with `fire_catapult()`.

Handy tricks:
- `drive(600, 0, 35)` and `turn_to(90, 30)`: the last number is the top speed. Go slower to be more accurate.
- The claw and catapult share two motors, so the robot does ONE thing at a time.
- Changing catapult level moves a cylinder. If you fire right after, put `wait(300, MSEC)` between.
- Every move returns True or False. `if not turn_to(90): return` stops the routine if that turn fails.
- To find which way the distance sensor points, run the old driver program in slot 4: it shows the
  distance on the brain screen. Wave a hand at each end of the robot and see which one changes it.

If a move runs out of time the routine keeps going, and the result screen shows TIMEOUT.

## How the robot fixes its own mistakes (the idea behind the numbers)

The robot always asks: "how far am I from where I should be?" That distance is the **error**.

- **KP** = how hard it pushes for each bit of error. Far away = push hard, close = push gently.
  Too high and it overshoots, like a car that brakes too late.
- **KD** = the brakes. It slows the robot down when the error is shrinking fast.
  Higher KD = smoother, less overshoot. Too high and it gets slow and jittery.
- **KI** = leave at 0.

While driving, the robot does TWO jobs at once, and each has its own numbers:

| Job | Numbers |
|---|---|
| How far to go | `DRIVE_...` |
| Stay pointed the right way | `HEADING_...` |

**Rule 1: after a turn, every drive must name the NEW heading.** After `turn_to(90)`, write
`drive(300, 90)`. If you write `drive(300, 0)` the robot fights to turn back to 0 while it drives.

## When it overshoots, first work out WHICH overshoot it is

| What you see | What it is | Try this, in this order |
|---|---|---|
| The nose swings left and right while driving | Heading overshoot | 1. `HEADING_KP` 1.5 to 1.0 to 0.7. 2. Set `HEADING_KD` to 0.05, then 0.1. 3. `HEADING_MAX_CORRECTION` 20 to 10. |
| It spins or lurches right at the start | Heading fix is too strong at low speed | Lower `HEADING_KP` and `HEADING_MAX_CORRECTION`. |
| It rolls past the stopping spot, then backs up | Distance overshoot | 1. `DRIVE_MAX_SPEED` 60 to 45. 2. `DRIVE_KP` 0.4 to 0.3. 3. `DRIVE_KD` 0.02 to 0.05. |
| It never fully fixes a drift | Heading fix too weak | Raise `HEADING_KP` a little. |

**How to tune:**
1. Change ONE number. Change it by about a third, not by 10 times.
2. Download, then test at least 3 times. "Sometimes" problems need several tries to see.
3. Write down: what you changed, what happened.
4. If it got better, keep going the same way. If it got worse, undo it.

Before tuning drives, make sure the Drive test really goes 500 mm (see `MM_PER_DEGREE` above).
A wrong distance scale makes everything else look wrong.

## If something is wrong (change ONE number, then test again)

| Problem | Change |
|---|---|
| Turn overshoots or wobbles | Lower `TURN_KP`, or raise `TURN_KD` |
| Turn too slow | Raise `TURN_KP` a little, then `TURN_MAX_SPEED` |
| Turn stops 1-3 degrees short | Raise `TURN_MIN_SPEED` |
| Drive overshoots | Lower `DRIVE_KP`, or raise `DRIVE_KD` |
| Drive too slow | Raise `DRIVE_KP`, then `DRIVE_MAX_SPEED` |
| Drive goes the wrong distance every time | Fix `MM_PER_DEGREE` (Drive test) |
| Drive stops a few mm short | Raise `DRIVE_MIN_SPEED` |
| Drifts sideways | Raise `HEADING_KP`. Also check `HEADING_DIRECTION`. |
| Wheels slip at the start | Lower `ACCEL_STEP` |
| "INERTIAL BUSY" at start | Stop the program, put the robot still on a flat surface, start it again and do not touch it. If it keeps happening, run `programs/sensor_test.py`. |
