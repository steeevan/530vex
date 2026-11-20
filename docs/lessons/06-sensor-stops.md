# Lesson 6: Letting sensors decide when to stop

**Big question:** How can walls and sensors fix the robot's mistakes?

**Functions in this lesson:** `back_until_bumper()`, `drive_until_distance()`, and using
`set_heading()`, in [`src/main.py`](../../src/main.py).

**Before this:** [Lesson 5](05-turning-and-driving.md).

---

## The idea

`drive()` and `turn_to()` measure the robot's **own** movement: wheel turns and the gyro. Small
mistakes creep in, like a wheel slipping, a bump on the field or a little gyro drift. Over a long
routine those mistakes add up.

Sailors had the same problem before GPS. They worked out their position from speed, direction and
time. That's called **dead reckoning**, and it slowly drifts. So whenever they saw a lighthouse,
they corrected their position.

For a robot, **the field is the lighthouse.** Walls don't move. When the robot touches a wall or sees
an object at a known distance, it knows exactly where it is again.

| | Measures | Good at | Weak at |
|---|---|---|---|
| `drive()`, `turn_to()` | the robot's own wheels and gyro | going exact distances anywhere | small errors add up |
| `back_until_bumper()`, `drive_until_distance()` | the real world | resetting errors | only works near a wall or object |

Good routines use both: wheels and gyro for most moves, and the field now and then to wipe out the
mistakes.

## Part A: `back_until_bumper()`

```python
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
```

It's the same loop shape as `drive()`, with a different way of stopping:

- **Stops when** the bumper is pressed, not after a distance.
- **No distance PID.** It just backs up at a steady, slow speed (`BUMPER_SPEED` = 20%).
- **`-abs(speed)`** means it always goes **backward**, even if someone passes a positive speed. The
  bumper is on the back of the robot, so going forward would never press it.
- **It still holds its heading** with the heading PID, so it backs up straight.
- **Time limit:** if nothing is hit within 4 seconds, it gives up and reports `bumper`.

**Why slowly?** A gentle hit presses the bumper reliably. The robot doesn't bounce off the wall, and
nothing gets bent.

### Lining up on a wall and resetting the heading

Once the robot's back is flat against a wall, two things are known for sure:

1. **Where it is:** its back is touching that wall.
2. **Which way it faces:** straight away from the wall.

So you can tell the gyro the true heading:

```python
back_until_bumper(90)
set_heading(90)     # "you are facing exactly 90 now"
```

Any drift the gyro built up so far is wiped out.

> **Careful:** `set_heading(90)` is only right if the robot really is flat against the wall, and the
> robot started the program square to the field. `back_until_bumper()` stops the moment the bumper
> clicks. If the robot arrives at an angle, its back might not be flat yet.

**Extension idea (not tested yet):** push a little longer so the back settles flat on the wall:

```python
back_until_bumper(90)
drive_motors(-20, -20)   # keep pushing gently
wait(300, MSEC)
brake_drive()
set_heading(90)
```

## Part B: `drive_until_distance()`

```python
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
```

- **`is_object_detected()` first.** If the sensor sees nothing, its distance number means nothing,
  so the program doesn't trust it.
- **Two close readings in a row.** One strange reading (a reflection, or a hand waving past) could
  stop the robot too early. Waiting for two in a row filters out one-off glitches. This is called
  **debouncing**.
- **The sign of `speed` picks the direction.** The team hasn't checked yet which end of the robot the
  sensor faces. Passing `30` or `-30` lets you choose without changing the function. (To find out,
  run the old driver program in slot 4. It shows the distance on the screen. Wave a hand at each
  end.)

### The math: how far past does it go?

The robot doesn't stop at the exact moment the sensor first sees the object:

1. It needs a **second** close reading, which is one more loop (20 ms) of driving.
2. After the brakes go on, it still **rolls a little** before it stops.

```
extra distance during one loop = speed × time
```

If the robot moves at 120 mm per second, then in 20 ms (0.02 s):

```
120 × 0.02 = 2.4 mm
```

That's small. But at 400 mm per second it's 8 mm, and rolling after braking is longer too. That's
why `SENSOR_SPEED` is slow (30%): **slower means a more exact stop.**

## Why it's built this way

- **Use the world to fix your own mistakes.** Wheels and gyros drift, but walls don't.
- **Never trust one reading.** Two in a row costs a tiny delay and prevents false stops.
- **The same safety rules as every move:** a time limit, heading hold, brake at the end, and
  True or False returned.
- **Be honest about what you don't know yet.** The program doesn't guess which way the sensor faces.
  It lets you choose with the sign of `speed`.

## Try it

1. **Which way does the sensor face?** Use the driver program's distance display (see Part B).
2. **Stop accuracy:** put a wall in front of the sensor. Run `drive_until_distance(150, 0, 30)` and
   measure the real distance from the sensor to the wall. Try again at speed 60. How much further
   did it go?
3. **Crooked wall test:** start the robot slightly crooked and run `back_until_bumper(0)`. Is the
   back flat against the wall? Try the extension idea from Part A.
4. **Design challenge:** write a routine that drives out, comes back, lines up on a wall, resets its
   heading, and then drives somewhere else. Is the second part more accurate than without the wall?

## Check your understanding

1. Why does `back_until_bumper()` use `-abs(speed)`?
2. What could go wrong if `drive_until_distance()` stopped after just one close reading?
3. At 200 mm per second, how far does the robot move in one 20 ms loop?
4. When is it safe to call `set_heading(90)` after `back_until_bumper(90)`?
5. What happens if the bumper never gets pressed?

<details>
<summary>Answers</summary>

1. So it always backs up, because the bumper is on the back. A positive speed would never press it.
2. One glitchy reading (a reflection, or a hand) could stop the robot in the wrong place.
3. 200 × 0.02 = 4 mm.
4. When the robot's back is really flat against the wall and it started the program square to the
   field.
5. After 4 seconds (`BUMPER_TIMEOUT_MS`) it stops, brakes, reports `bumper` and returns False.

</details>

## Teacher notes

- **Time:** 45 minutes.
- **The lighthouse story** helps students see *why* we touch walls during a routine. Ask: "where on
  our field could the robot reset itself?"
- **Common mistake:** calling `set_heading()` when the robot isn't really square. The robot then
  "corrects" itself into the wrong heading. Show it on purpose.
- **Good discussion:** what's better for stopping near a wall, `drive(...)` or
  `drive_until_distance(...)`? (It depends: sensors are exact near objects, wheels work anywhere.)
