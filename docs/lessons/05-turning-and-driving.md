# Lesson 5: Turning and driving

**Big question:** How do the pieces from lessons 2 to 4 fit together into `turn_to()` and `drive()`?

**Functions in this lesson:** `drive_motors()`, `brake_drive()`, `heading_correction()`,
`turn_to()`, `drive()` in [`src/main.py`](../../src/main.py).

**Before this:** [Lesson 4](04-smooth-and-done.md).

---

## The idea

You now have all the parts:

| Part | Lesson | Job |
|---|---|---|
| `heading_now()`, `wheel_degrees()`, `angle_diff()` | 2 | Measure where the robot is |
| `PID` | 3 | Turn the error into power |
| `ramp()`, `keep_moving()`, `Settle`, time limits | 4 | Start smoothly, keep moving, know when it's done, don't get stuck |

`turn_to()` and `drive()` are just these parts run together in a loop.

## Part A: sending power to the wheels

```python
def drive_motors(left, right):
    # Left faster than right = turns clockwise.
    L.spin(FORWARD, clamp(left, -100, 100), PERCENT)
    R.spin(FORWARD, clamp(right, -100, 100), PERCENT)


def brake_drive():
    L.stop(BRAKE)
    R.stop(BRAKE)
```

This robot steers like a tank: it has no steering wheel, only a left side and a right side. It turns
by running them at different speeds.

| `drive_motors(...)` | What the robot does |
|---|---|
| `(50, 50)` | drives straight forward |
| `(-30, -30)` | drives straight backward |
| `(50, -50)` | spins in place clockwise (right) |
| `(-50, 50)` | spins in place counterclockwise (left) |
| `(55, 45)` | drives forward, curving right |

`clamp()` makes sure neither side is ever asked for more than 100%.

## Part B: `turn_to()`

```python
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
```

**Before the loop:** make a fresh PID and Settle, note the start time, and start at speed 0.

**Each loop (every 20 ms), until time runs out:**

1. **Measure:** `error` = the shortest turn left to do.
2. **Decide:** `wanted` = how much power PID asks for.
3. **Done?** If the robot has stayed close enough for long enough, stop the loop.
4. **Adjust:** if it's close enough right now, use 0 power and let it settle. If not, cap the power
   at `max_speed` and make sure it's at least `TURN_MIN_SPEED`.
5. **Smooth:** `ramp()` limits how fast the power can rise.
6. **Act:** left side forward and right side backward (or the reverse) to spin in place.
7. **Wait** 20 ms, then go again.

**After the loop:** brake, report a problem if it ran out of time, and return True or False.

Every move in the program follows the same pattern: **measure, decide, act, wait, repeat.** Robot
engineers call it the **sense, think, act** loop.

### The math: the first loop of `turn_to(90)`

The robot faces 20°.

```
error   = angle_diff(90, 20) = 70
wanted  = 0.9 × 70 = 63      (first loop, so no D yet)
capped  = 50                 (TURN_MAX_SPEED)
ramped  = 0 + 4 = 4          (speed was 0, ACCEL_STEP is 4)
drive_motors(4, -4)
```

Even though PID wants 63%, the first loop only uses 4%. Over the next loops the power climbs 8, 12,
16... up to 50, then PID lowers it as the robot gets close.

## Part C: `drive()`, two jobs at once

While driving, the robot has to do two things:

1. go the right **distance**, and
2. stay pointed the right **way** (drifting is easy, since one wheel slips or one motor is a bit
   stronger).

So `drive()` uses **two PIDs**: one for distance, one for heading.

```python
def heading_correction(pid, target_heading):
    error = angle_diff(target_heading, heading_now())
    return clamp(pid.update(error), -HEADING_MAX_CORRECTION, HEADING_MAX_CORRECTION)
```

```python
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
```

What's new compared with `turn_to()`:

- **`start_degrees`:** the wheel position when the drive starts. The distance moved is measured from
  there, so each drive counts from 0 without resetting the motors.
- **`moved_mm`:** wheel degrees turned since the start, changed to millimeters (lesson 2).
- **A negative distance drives backward.** `drive(-400, 90)` gives a negative error, so a negative
  speed.
- **`turn`:** the heading PID's steering, capped at ±`HEADING_MAX_CORRECTION` (20%).
- **`drive_motors(speed + turn, speed - turn)`:** mixes "go forward" with "steer."

### The math: mixing speed and steering

```
left  = speed + turn
right = speed − turn
```

Look what happens when you add and subtract them:

```
(left + right) ÷ 2 = speed     ← forward progress is unchanged
(left − right) ÷ 2 = turn      ← the difference steers
```

So steering never speeds up or slows down the drive. It only shifts power from one side to the
other.

**Example:** driving at 60%, aiming for heading 0, but the robot has drifted to −2° (a little to the
left).

```
heading error = angle_diff(0, -2) = 2
turn          = 1.5 × 2 = 3              (HEADING_KP = 1.5)
left          = 60 + 3 = 63
right         = 60 − 3 = 57
```

The left side goes a bit faster, so the robot curves right, back to 0. Check it:
(63 + 57) ÷ 2 = 60 and (63 − 57) ÷ 2 = 3.

**It works backward too.** Driving at −40% with turn = 3: left = −37, right = −43. The left side
is still "more forward" than the right, so the robot still rotates clockwise. One formula works in
both directions.

### Why cap the steering at 20%?

The heading PID is there to fix **small** drifts. If the robot is way off, that's a job for
`turn_to()`. Without the cap, a big heading error could take over the drive and spin the robot.

## Part D: always name the heading

```python
turn_to(90)
drive(300, 90)    # right: the new heading
drive(300, 0)     # wrong!
```

After `turn_to(90)`, writing `drive(300, 0)` gives a heading error of −90. The steering is capped at
−20%, but that's still a lot. The robot curves back toward 0 while it drives and ends up somewhere
you didn't plan.

### Why every move uses headings measured from the start

Every heading is measured from where the robot faced at the start (0). Compare two ways of doing
four right turns:

| Way | Turn 1 | Turn 2 | Turn 3 | Turn 4 | Final error |
|---|---|---|---|---|---|
| **Relative:** "turn 90 more" each time, 1° short each time | 89 | 178 | 267 | 356 | **4°** |
| **Absolute:** `turn_to(90)`, `turn_to(180)`..., 1° short each time | 89 | 179 | 269 | 359 | **1°** |

With relative turns, each small mistake is added to the last one. With absolute turns, each turn
aims at a fixed target measured from the start, so turn 2 also fixes turn 1's mistake. **Errors
don't add up.** That's why the **Turn test** turns to 90, 180, 270 and 360.

## Part E: True or False

Both moves return `done`: True if they arrived, False if they ran out of time. A routine can use
that:

```python
if not turn_to(90):
    return          # stop the routine: the turn failed, so the next moves would be wrong
```

## Why it's built this way

- **Built from small, tested parts.** `turn_to()` and `drive()` contain almost no new math. They
  combine helpers you already understand.
- **The same loop shape everywhere.** Once you can read `turn_to()`, you can read every other move.
- **Two controllers, one job each.** One PID handles distance and one handles heading. Each is
  simple, and each can be tuned separately.
- **Always brake at the end,** whether the move worked or not.
- **Headings measured from the start,** so errors don't pile up during a long routine.

## Try it

1. **Push test:** set `HEADING_KP = 0` and run **Drive test**. Gently push the side of the robot
   while it drives. Then set it back to 1.5 and push again. What's different?
2. **Make the bug on purpose:** write `turn_to(90)` then `drive(300, 0)` in `routine()`. Predict
   what happens, run it, then fix it.
3. **On paper:** fill in left and right for these: speed 50, turn 5 / speed 50, turn −5 /
   speed −30, turn 4.
4. **Trace one loop:** for `drive(600, 0)`, the robot has moved 580 mm and faces −1°. Work out the
   error, P, the turn, and left and right (ignore D).

## Check your understanding

1. `speed = 40`, `turn = -5`. What are left and right? Which way does the robot curve?
2. Why does `drive()` record `start_degrees` at the start?
3. What happens if you write `turn_to(90)` and then `drive(300, 0)`?
4. Why is the steering capped at 20%?
5. Why does `turn_to()` call `drive_motors(speed, -speed)`?

<details>
<summary>Answers</summary>

1. Left = 35, right = 45. The right side is faster, so it curves left (counterclockwise).
2. So it measures the distance moved during *this* drive, starting from 0, without resetting the
   motors.
3. The heading PID sees a 90° error and steers (up to 20%) back toward 0 while driving. The robot
   curves off course.
4. So steering can only fix small drifts and can't take over the drive. Big direction changes are
   `turn_to()`'s job.
5. One side forward and the other backward at the same speed spins the robot in place.

**Try it 4:** error = 600 − 580 = 20 mm, so P = 0.4 × 20 = 8%. Turn: angle_diff(0, −1) = 1, so
turn = 1.5 × 1 = 1.5%. Left = 9.5, right = 6.5. (8% is right at `DRIVE_MIN_SPEED`, so
`keep_moving()` keeps it at 8.)

</details>

## Teacher notes

- **Time:** 45 to 60 minutes.
- **Draw the field** on the board or on paper and walk through the routine move by move, writing the
  heading at each step.
- **The most common bug** in student routines is the wrong heading after a turn (Part D). Make it on
  purpose (Try it 2) so they recognize it later.
- **Tracing a loop with real numbers** (Try it 4) is the best way to check understanding. Do one
  together, then let pairs do another.
