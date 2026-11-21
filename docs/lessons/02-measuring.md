# Lesson 2: Measuring where the robot is

**Big question:** How does the robot know how far it went and which way it's facing?

**Functions in this lesson:** `wheel_degrees()`, `heading_now()`, `set_heading()`, `angle_diff()`,
`wait_for_inertial()`, `now_ms()`, `clamp()` in [`src/main.py`](../../src/main.py).

**Before this:** [Lesson 1](01-big-picture.md).

---

## The idea

The robot can't see the field. It only knows what its sensors tell it. Two measurements do almost
all the work:

1. **How far the wheels have turned.** Every VEX motor counts how many degrees it has spun.
2. **Which way the robot faces.** The brain has a built-in inertial sensor that feels the robot
   turning.

Everything in lessons 3 to 6 is built on these two numbers. If they're wrong, every move is wrong.

## Part A: distance from wheel turns

### The code

```python
def wheel_degrees():
    return (L.position(DEGREES) + R.position(DEGREES)) / 2.0
```

It adds the left and right wheel positions and divides by 2, which gives the **average**.

Why the average?

- **Driving straight:** both sides turn the same amount, so the average is the same too.
- **Turning in place:** the left side goes forward (+) and the right goes backward (−). They cancel
  out, so the average is about 0. That's right, because the robot didn't move anywhere, it only
  turned.
- **Steering a little while driving:** one side turns a bit more than the other. The average gives
  the distance traveled by the middle of the robot.

### The math: degrees to millimeters

When a wheel turns once (360°), the robot rolls forward one **circumference** of the wheel.

```
circumference = π × diameter
```

This robot is assumed to have VEX IQ wheels made to roll **200 mm per turn**, so:

```
mm per degree = 200 mm ÷ 360° = 0.556 mm
```

That's the setting `MM_PER_DEGREE = 0.556`.

**Example:** the wheels turned 1080° (three full turns).

```
1080 × 0.556 = 600 mm (about)
```

### Fixing the number with a drive test

The 0.556 comes from math, but real robots are messy. Tires squish, wheels slip, and gears change
the numbers. So instead of trusting the math, **measure it**:

1. Make `routine()` do only `drive(500, 0)`: put that line at the top of `routine()`, followed by
   `return` (the [robot guide](../robot-guide.md) shows how). Run the program. The robot is told
   to drive 500 mm.
2. Measure how far it really went. Call that D.
3. Work out the new number:

```
new MM_PER_DEGREE = old MM_PER_DEGREE × D ÷ 500
```

**Example:** the robot only went 450 mm.

```
new = 0.556 × 450 ÷ 500 = 0.500
```

Why does this work? The robot *thought* it went 500 mm but really went 450, so each degree of wheel
turn is only worth 450/500 (= 0.9) of what we thought. With the smaller number, the robot turns its
wheels more and really goes 500 mm.

## Part B: which way the robot faces

### How the inertial sensor works

The inertial sensor has a **gyroscope**. A gyroscope doesn't measure an angle directly. It measures
**how fast** the robot is turning, in degrees per second. The brain adds up all those tiny turns,
many times a second, to get the total angle.

It's like walking with your eyes closed and counting your steps. It works well, but small mistakes
slowly add up. That slow error is called **drift**.

### Why the robot must stay still at the start

When the program starts, the sensor measures what "not turning" looks like. This is called
**calibrating**. If someone bumps the robot during it, the sensor learns the wrong "zero" and the
heading drifts for the whole run.

```python
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
```

- It shows "HANDS OFF!" and waits while the sensor is still calibrating.
- If it takes longer than `INERTIAL_WAIT_MS` (8 seconds), something is wrong. It shows a warning
  instead of waiting forever.

**A true story from this robot:** VEX has a `calibrate()` command, so you'd think the program
should call it. But when the team tested it with `programs/sensor_test.py`, `calibrate()` got stuck
and never finished. The test also showed the brain calibrates by itself when a program starts, so
the program just waits for that. Testing beat guessing.

### heading() vs rotation()

The sensor gives two numbers:

| You turn the robot... | `heading()` says | `rotation()` says |
|---|---|---|
| 90° right | 90 | 90 |
| one full turn right | 0 | 360 |
| one and a quarter turns right | 90 | 450 |
| 30° left | 330 | −30 |

`heading()` wraps around like a compass: after 359 it jumps back to 0. `rotation()` keeps counting.

The program uses `rotation()`. A sudden jump from 359 to 0 would make the robot think it had spun
359° in one fiftieth of a second. Lesson 3's PID would react to that by slamming the motors.

```python
def heading_now():
    # rotation() has no 359 -> 0 jump
    return brain_inertial.rotation(DEGREES) * HEADING_DIRECTION


def set_heading(value):
    brain_inertial.set_rotation(value * HEADING_DIRECTION, DEGREES)
```

- `heading_now()` reads the angle. In this program, **turning clockwise (right) makes it bigger**.
- `HEADING_DIRECTION` is 1 or −1. If the sensor happens to count the other way, setting it to −1
  flips the sign, because multiplying by −1 turns 90 into −90. One setting fixes every move.
- `set_heading(90)` tells the robot "you're facing 90 now." Lesson 6 uses it after lining up on a
  wall.

## Part C: the shortest way around

The robot is facing 350° and wants to face 10°. Should it turn 340° to the left, or 20° to the right?
Obviously 20° right. `angle_diff()` works that out:

```python
def angle_diff(target, current):
    # Turn needed (clockwise = +), always the short way: -180..+180
    diff = (target - current) % 360
    if diff > 180:
        diff -= 360
    return diff
```

1. `target - current` is the turn needed, but it might be the long way around.
2. `% 360` (modulo) means "the remainder after taking away whole circles." In Python the answer is
   always between 0 and 359.99, even for negative numbers. That's the turn needed **if you go
   clockwise**.
3. If that's more than 180°, going the other way is shorter, so subtract 360. That gives a negative
   number, which means counterclockwise.

### The math: worked examples

| Target | Current | target − current | % 360 | Answer | Meaning |
|---|---|---|---|---|---|
| 90 | 0 | 90 | 90 | **90** | turn 90° right |
| 0 | 90 | −90 | 270 | **−90** | turn 90° left |
| 10 | 350 | −340 | 20 | **20** | turn 20° right |
| −90 | 170 | −260 | 100 | **100** | turn 100° right |
| 270 | 0 | 270 | 270 | **−90** | turn 90° left (same as facing −90) |

Modulo is "clock math." 13 o'clock is 1 o'clock because 13 % 12 = 1. Angles work the same way with
360.

> **Careful:** not every language does this. In C or Java, `-90 % 360` gives −90, not 270. Python
> always gives an answer with the same sign as the number you divide by.

## Part D: two small helpers

```python
def now_ms():
    return clock.time(MSEC)


def clamp(value, low, high):
    return min(max(value, low), high)
```

- `now_ms()` gives the time since the program started, in milliseconds. Moves use it for time
  limits.
- `clamp()` keeps a number inside limits. Read it from the inside out: `max(value, low)` raises the
  number to at least `low`, then `min(..., high)` lowers it to at most `high`.

| Call | Answer |
|---|---|
| `clamp(81, -50, 50)` | 50 |
| `clamp(30, -50, 50)` | 30 |
| `clamp(-120, -100, 100)` | −100 |

## Why it's built this way

- **One measurement, one function.** If the robot gets a different sensor, only `heading_now()`
  needs to change, not every move.
- **One setting fixes a whole problem.** `HEADING_DIRECTION` and `MM_PER_DEGREE` are settings. They
  aren't numbers buried in many lines.
- **Measure, don't trust the math.** A drive test checks `MM_PER_DEGREE` on the real robot.
- **Pick the number that's easiest to work with.** `rotation()` has no jumps, and `angle_diff()`
  handles the "shortest way" problem in one place.

## Try it

1. **Heading direction:** run `programs/sensor_test.py` (see the [robot guide](../robot-guide.md)).
   On its first screen (TEST 1/4), turn the robot 90° clockwise by hand. Does `rot` go up to about
   90? If it goes down, set `HEADING_DIRECTION = -1`.
2. **Drift test (same screen):** spin the robot one full turn by hand and put it back where it
   started. Does `rot` go back to about 0 (or 360)? Leave the robot still for one minute. Does the
   number creep?
3. **Drive test:** put `drive(500, 0)` and `return` at the top of `routine()`. Measure the real
   distance, then work out a new `MM_PER_DEGREE`.
4. **On paper:** roll a wheel one full turn along a ruler. Is it really 200 mm?

## Check your understanding

1. The wheels turned 720° and `MM_PER_DEGREE` is 0.556. How far did the robot go?
2. The robot spins in place: left +180°, right −180°. What does `wheel_degrees()` return?
3. What is `angle_diff(10, 350)`?
4. What is `angle_diff(0, 90)`, and which way will the robot turn?
5. Why does the program use `rotation()` and not `heading()`?
6. A drive test was told 500 mm but went 520 mm. `MM_PER_DEGREE` was 0.556. What's the new value?

<details>
<summary>Answers</summary>

1. 720 × 0.556 = about 400 mm.
2. (180 + −180) ÷ 2 = 0.
3. (10 − 350) % 360 = −340 % 360 = 20. Turn 20° right.
4. (0 − 90) % 360 = 270, which is more than 180, so 270 − 360 = −90. Turn 90° left.
5. `heading()` jumps from 359 to 0. That looks like a huge sudden turn and confuses the PID.
   `rotation()` counts smoothly.
6. 0.556 × 520 ÷ 500 = about 0.578.

</details>

## Teacher notes

- **Time:** 45 minutes. Part C works well as a paper exercise first.
- **Hands-on:** bring a wheel and a ruler. Rolling one turn makes "circumference" real.
- **Modulo:** use a clock face. Most students already know that 3 hours after 11 o'clock is
  2 o'clock.
- **Common confusion:** heading vs rotation. The table in Part B helps. Run
  `programs/sensor_test.py`, spin the robot by hand on its first screen, and let them see `rot`
  pass 360 while `head` jumps back to 0.
- **Connect to math class:** circumference (π × d), ratios (the drive test fix), negative numbers.
