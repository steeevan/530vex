# Lesson 1: The big picture

**Big question:** How is the program organized, and what happens when it starts?

**In this lesson:** the file's sections, `setup_motors()`, `routine()`, `run_routine()`, and the
last few lines of [`src/main.py`](../../src/main.py).

---

## The idea

`src/main.py` is about 600 lines long. Nobody should read it top to bottom on day one. First learn
its **shape**: which parts it has, what each part is for, and which parts you're allowed to change.

Here's a surprise: **almost the whole file is definitions.** A `def` tells Python "here's how to do
something", but it doesn't do it yet. Nothing on the robot moves until the last few lines of the
file.

## The sections of the file

From top to bottom:

| Section | What's in it | Edit it? |
|---|---|---|
| Robot configuration | Which motor or sensor is plugged into which port | Only if the wiring changes |
| `SETTINGS` | All the numbers: speeds, distances, times, tuning | **Yes** |
| `routine()` | The moves the robot does | **Yes** |
| "DON'T EDIT BELOW THIS LINE" | The engine: everything that makes the moves work | Only when you know why |
| Helpers (lessons 2 to 4) | Time, angles, PID, settling | |
| Drive base (lesson 5) | `turn_to()`, `drive()` | |
| Sensor moves (lesson 6) | `back_until_bumper()`, `drive_until_distance()` | |
| Mechanisms (lesson 7) | Claw and catapult | |
| Brain screen (lesson 8) | What the brain shows: HANDS OFF, the done screen, errors | |
| Start: `run_routine()` and the last lines | Start the program and run the routine | |

## The code

### Robot configuration

```python
L_motor_a = Motor(Ports.PORT5, False)
L_motor_b = Motor(Ports.PORT6, False)
L = MotorGroup(L_motor_a, L_motor_b)
R_motor_a = Motor(Ports.PORT11, True)
R_motor_b = Motor(Ports.PORT12, True)
R = MotorGroup(R_motor_a, R_motor_b)
```

- `Motor(Ports.PORT5, False)` means "there's a motor in port 5, and it is **not** reversed."
- The right motors say `True` (reversed). They're mounted as a mirror image of the left ones, so
  spinning "forward" would push the robot backward. Marking them reversed here means the rest of
  the program can say `FORWARD` for both sides and mean the same thing.
- `MotorGroup` joins two motors so they act as one. `L` is the whole left side, `R` the right.

The rest of the configuration names the other devices: `C_L` and `C_R` (the claw and catapult
motors), `pneumatic_9` (the air cylinders), `distance_3` (distance sensor), `Bumper_1` (bumper) and
`brain_inertial` (the heading sensor built into the brain).

### Settings

```python
TURN_KP = 0.9            # % per degree of error (higher = turns harder)
...
TURN_MAX_SPEED = 50
...
DRIVE_MAX_SPEED = 60
```

Settings are written in `ALL_CAPS`. In Python that's a signal that says "this number doesn't change
while the program runs." All of them sit at the top of the file so you can tune the robot without
digging through the engine.

### The routine

This is the start of the team's match routine:

```python
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
    # ...
```

A routine is a list of moves, done **one at a time, top to bottom**. Each move finishes before the
next one starts. `drive(-50, 0, 100)` doesn't return until the robot has backed up 50 mm (or run
out of time).

- A **negative** distance drives backward.
- The second number is the **heading** to face while driving (more in lesson 5).
- The third number, when it's there, is the **top speed** in %. Without it, the move uses the
  speed from `SETTINGS`.
- Lines starting with `#` are comments that split the routine into steps, like "shoot the preload".

The moves read almost like English. That's on purpose: the hard work is hidden inside the
functions, so the routine stays easy to read and change.

**Before the program starts,** the team arms the catapult and loads the preload by hand.
`start_mechanisms()` doesn't fire anything (lesson 7).

### Getting the motors ready

```python
def setup_motors():
    L.set_stopping(BRAKE)
    R.set_stopping(BRAKE)
    L.set_max_torque(100, PERCENT)
    R.set_max_torque(100, PERCENT)
    C_L.set_max_torque(100, PERCENT)
    C_R.set_max_torque(100, PERCENT)
```

- `BRAKE` makes a motor resist turning when it stops, so the robot stops quickly. The other choice,
  `COAST`, lets the wheels roll freely, so the robot glides past where it should stop.
- `set_max_torque(100, PERCENT)` lets every motor use its full strength.

### The start: the program begins here

There is **no menu**. When you start the program, the routine runs right away. `run_routine()` does
everything in order:

```python
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
```

```mermaid
flowchart TD
    A["Program starts"] --> B["setup_motors()<br/>brake mode, full strength"]
    B --> C["wait_for_inertial()<br/>HANDS OFF while the sensor gets ready"]
    C --> D["set_rotation(0)<br/>heading 0 = the way the robot faces now"]
    D --> E["routine()<br/>your moves"]
    E --> F["show_result()<br/>ROUTINE DONE screen"]
    E -->|"something crashes"| G["show_error()<br/>ERROR screen"]
    F --> H["while True<br/>the screen stays up until you press X"]
    G --> H
```

1. `setup_motors()` gets the motors ready.
2. `wait_for_inertial()` waits while the heading sensor gets ready. The robot must be still
   (lesson 2 explains why).
3. `set_rotation(0, DEGREES)` makes the way the robot faces **right now** heading 0. So line the
   robot up **before** you start the program.
4. It shows "RUNNING", notes the time, and runs your `routine()`.
5. `show_result()` shows the done screen: how long the routine took, and whether any move ran out
   of time (lesson 8).

The last lines are the only ones outside a `def`, so they're the ones that actually run:

- **`try` / `except`:** if anything inside `run_routine()` crashes, Python jumps to the `except`
  part. `show_error()` stops the robot and shows the error **on the brain screen**, so you can read
  it without a computer (lesson 8).
- **`while True`:** this loop does nothing, forever. It keeps the program running so the last
  screen (done or error) stays up. You stop the program with the brain's X button.

To test one part of the robot (a drive, a turn, the claw), the [robot guide](../robot-guide.md)
shows a trick: put the test at the top of `routine()`, followed by `return`.

## The math: time on a robot

The program measures time in **milliseconds** (ms). 1000 ms = 1 second.

Most loops in the program wait 20 ms each time around (`LOOP_MS = 20`):

```
loops per second = 1000 ms ÷ 20 ms = 50
```

So the robot checks its sensors and fixes its power **50 times every second**. That's fast enough to
steer smoothly, and slow enough to give the sensors time to update.

`run_routine()` goes the other way: it divides by 1000 to turn milliseconds into seconds for the
done screen. A routine that took 23,400 ms shows as 23,400 ÷ 1000 = 23.4 seconds.

## Why it's built this way

- **The parts you change are separate from the parts you don't.** Students edit `SETTINGS` and
  `routine()` at the top. A mistake there is easy to find, and it can't break the engine.
- **Moves have names that say what they do.** `back_until_bumper(90)` explains itself.
  `L.spin(FORWARD, -20, PERCENT)` doesn't.
- **Define first, run last.** Python reads the file from top to bottom, and a function has to be
  defined before it's called. Putting the "start" lines at the very bottom means every function
  already exists when they run.
- **Crashes show up on the brain.** The whole run is inside `try` / `except`, so an error appears on
  the brain screen instead of only on the computer.
- **The file is kept small.** The brain has very little memory (lesson 9). That's why long
  explanations live in these lessons and not in the code.

## Try it

1. Open `src/main.py`. Find the start of each section in the table above and write down its line
   number.
2. On paper, plan a routine that drives in a square and ends where it started. Then type it at the
   **top** of `routine()`, followed by `return`. `return` ends the function right there, so the
   match moves under it are skipped, not lost:

   ```python
   def routine():
       drive(400, 0)
       turn_to(90)
       drive(400, 90)
       turn_to(180)
       drive(400, 180)
       turn_to(270)
       drive(400, 270)
       turn_to(360)
       return               # TEST - delete these lines when done
       start_mechanisms()   # (the match routine, skipped for now)
   ```

   Mark the start position with tape. Run it, then measure how far from the tape the robot ends up.
   Delete your test lines when you're done.

## Check your understanding

1. Which two parts of the file are meant to be edited?
2. Why are the right motors marked `True`?
3. What would happen if you took away the `try` / `except` and `routine()` crashed?
4. A loop waits 10 ms each time. How many times per second does it run?
5. In the routine, does `turn_to(-32)` start while `drive(-50, 0, 100)` is still driving?

<details>
<summary>Answers</summary>

1. `SETTINGS` (the numbers) and `routine()` (the moves).
2. They're mounted as a mirror image of the left motors. Reversing them means `FORWARD` moves the
   robot forward on both sides.
3. The program would stop with the error. The brain would only say "Program error" and point you
   to the console, which is on the computer. Our ERROR screen would never appear, so at a
   competition you couldn't tell what went wrong.
4. 1000 ÷ 10 = 100 times per second.
5. No. Each move finishes before the next one starts.

</details>

## Teacher notes

- **Time:** 30 to 40 minutes. You don't need the robot, but the square routine is a fun end to
  the lesson if you have one.
- **Common misunderstanding:** students think the code "runs" each `def` as Python reads it. Show
  that nothing moves until the last few lines. A good demo: put `print("hi")` inside a function
  that's never called.
- **Common mistakes in `routine()`:** wrong indentation, a missing `)`, and putting the routine's
  moves outside the function.
- **Connect to lesson 9:** ask "why do you think the settings are at the top?" now, and come back to
  it at the end.
