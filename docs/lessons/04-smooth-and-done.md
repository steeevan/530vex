# Lesson 4: Smooth starts and clean stops

**Big question:** How does the robot speed up without slipping, and how does it know it's done?

**Functions in this lesson:** `ramp()`, `keep_moving()`, `Settle`, `report_problem()`, and the
time limits, in [`src/main.py`](../../src/main.py).

**Before this:** [Lesson 3](03-pid.md).

---

## The idea

PID (lesson 3) works out how much power to use. But four problems are left:

1. **Jumping straight to full power makes the wheels slip.**
2. **Close to the target, the power gets too small to move the robot at all.**
3. **The error is never exactly 0, so when is the move finished?**
4. **What if the robot gets stuck and never arrives?**

Each problem gets its own small helper. Lesson 5 puts them all together.

## Problem 1: speeding up gently with `ramp()`

### Why it matters

If the motors go from 0% to 60% in one instant, the wheels spin before the robot gets going, like a
car "burning rubber." That's bad for two reasons:

- The motors count wheel turns that didn't move the robot, so `drive()` thinks it went further than
  it did and **stops short**.
- The sudden jerk can twist the robot off its heading.

### The code

```python
def ramp(current, target, step):
    # Slowing down is instant. Speeding up / reversing is limited to step.
    if abs(target) <= abs(current) and target * current >= 0:
        return target
    if target > current + step:
        return current + step
    if target < current - step:
        return current - step
    return target
```

- `current` is the power used last loop. `target` is what PID wants now. `step` is the most it may
  change in one loop (`ACCEL_STEP = 4`).
- **The first `if`: slowing down is allowed instantly.** If PID wants to slow down, it's because
  the robot is getting close. Delaying the brakes would cause overshoot.
- **The other two `if`s: speeding up or reversing** may only change by `step` each loop.

### The sign trick

How does the code know "slowing down" from "reversing"? With `target * current >= 0`:

| target | current | target × current | Meaning |
|---|---|---|---|
| + | + | + | same direction |
| − | − | + | same direction |
| + | − | − | opposite directions |
| anything | 0 | 0 | stopped, so OK |

A negative times a negative is positive, so the product is only negative when the two numbers point
opposite ways. Slowing down means the **same direction** and a **smaller size**.

### The math

| Call | What happens | Answer |
|---|---|---|
| `ramp(20, 50, 4)` | speeding up, limited | 24 |
| `ramp(50, 30, 4)` | slowing down, instant | 30 |
| `ramp(10, -30, 4)` | reversing, limited | 6 |
| `ramp(-20, -10, 4)` | slowing down backward, instant | −10 |

**How long does it take to get from 0% to 60%?**

```
loops   = 60 ÷ 4  = 15 loops
time    = 15 × 20 ms = 300 ms
```

Less than a third of a second, but smooth enough that the wheels grip.

## Problem 2: too little power to move, fixed by `keep_moving()`

### Why it matters

Motors need a certain amount of power just to start moving. That's because of **friction**. At 3%
power the motor hums but the robot doesn't budge. Close to the target, PID asks for tiny amounts of
power (0.9 × 3° = 2.7%), so the robot would stall just short and never finish.

### The code

```python
def keep_moving(speed, min_speed, error):
    # Too little power to move? Use min_speed.
    if abs(speed) < min_speed:
        if error > 0:
            return min_speed
        return -min_speed
    return speed
```

If the power is too small, it's raised to `min_speed`, pointing the way the error says to go.

**Example:** turning, 5° left to go. PID says 0.9 × 5 = 4.5%. That's below `TURN_MIN_SPEED` (6), so
the robot uses 6%.

**The trade-off:**
- `MIN_SPEED` **too low:** the robot stalls before it arrives and runs out of time.
- `MIN_SPEED` **too high:** it zooms past the target, comes back, zooms past again...

## Problem 3: knowing when it's done, with `Settle`

### Why not just check `error == 0`?

The error is a decimal number and the sensors are a little noisy. The error will be 0.03 or −0.2,
almost never exactly 0. So the robot uses a **tolerance**: close enough counts.

- `TURN_TOLERANCE = 1.0` (within 1 degree)
- `DRIVE_TOLERANCE = 5` (within 5 mm)

### Why also wait?

The robot might zoom **through** the "close enough" window while still moving fast, on its way to
overshooting. Passing through isn't arriving. So the robot has to **stay** inside the window for
`SETTLE_MS` (120 ms, that's 6 loops) before the move counts as done.

### The code

```python
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
```

- `self.inside` is True when the robot is close enough right now.
- `self.since` is the time it entered the window. If the robot leaves the window, `since` resets to
  `None` and the clock starts over.
- It returns True only when `now − since` reaches 120 ms.

### The math: a timeline

A turn with tolerance 1° and settle time 120 ms:

| Time (ms) | Error | Inside? | `since` | now − since | Done? |
|---|---|---|---|---|---|
| 0 | 3.0° | no | None | | no |
| 20 | 0.8° | yes | 20 | 0 | no |
| 40 | 0.4° | yes | 20 | 20 | no |
| 60 | −1.3° | **no** (wobbled past) | None | | no |
| 80 | −0.6° | yes | 80 | 0 | no |
| ... | | yes | 80 | | no |
| 200 | −0.2° | yes | 80 | 120 | **yes** |

The wobble at 60 ms restarted the clock. That's exactly what we want, because the robot wasn't
steady yet.

## Problem 4: getting stuck, solved with time limits

### Why it matters

What if the robot is pushing against a wall or a game piece? Without a time limit it would push
**forever**. The rest of the routine would never run, and the motors would get hot.

So every move has a time limit. When time runs out, the move stops, brakes, reports the problem, and
lets the routine carry on.

| Move | Time limit |
|---|---|
| `turn_to()` | `TURN_TIMEOUT_MS` = 3000 ms |
| `drive()` | `DRIVE_TIME_BASE_MS` + mm × `DRIVE_TIME_PER_MM` |
| `back_until_bumper()` | 4000 ms |
| `drive_until_distance()` | 4000 ms |
| catapult wind-down, claw arm | 2000 ms each |

A drive's limit depends on how far it goes, because longer drives need more time:

```
drive(600, 0):   1500 + 600 × 8 = 6300 ms
drive(-400, 90): 1500 + 400 × 8 = 4700 ms   (uses the size, so −400 counts as 400)
```

### Reporting problems

```python
problem_count = 0        # moves that ran out of time
last_problem = ""
# ...

def report_problem(name):
    global problem_count, last_problem
    problem_count += 1
    last_problem = name
```

- When a move runs out of time it calls something like `report_problem("drive")`.
- The done screen at the end of the routine then shows `1 TIMEOUT(S)` and `last: drive`, so you
  know which move had trouble (lesson 8).
- There's no need to reset the count. It starts at 0 every time the program starts, and the routine
  runs once per start.
- `global` means "I want to change the variable that lives outside this function." Without it,
  Python would make a new local variable and the count outside would never change.

## Why it's built this way

- **One small helper per problem.** Each one is short enough to understand on its own, and lesson 5
  combines them.
- **Expect things to go wrong.** Robots get bumped, stuck and blocked. Time limits make sure one bad
  move can't ruin the whole routine. This is called **defensive programming**.
- **Don't hide problems.** A move that runs out of time says so on the screen, so you can fix the
  cause instead of guessing.
- **Every limit is a named setting,** so you can tune it without reading the code.

## Try it

For these, put the test at the top of `routine()`, followed by `return` (the
[robot guide](../robot-guide.md) shows how).

1. **Slip test:** set `ACCEL_STEP = 20` and run the drive test (`drive(500, 0)`) on a smooth floor.
   Watch the wheels at the start and measure the distance. Put it back to 4 and compare.
2. **Minimum speed:** set `TURN_MIN_SPEED = 0` and run the turn test (`turn_to(90)`, `turn_to(180)`,
   `turn_to(270)`, `turn_to(360)`). Does it stop short or show a TIMEOUT? Then try 15. Does it
   wobble? Put it back to 6.
3. **Time limit:** gently hold the robot during the drive test so it can't finish. What does the
   done screen say?
4. **On paper:** write down the power for each loop of `ramp()` going from 0 to 60 with step 4.

## Check your understanding

1. With `ACCEL_STEP = 4` and 20 ms loops, how long does it take to go from 0% to 40%?
2. What does `ramp(30, -30, 4)` return? Why?
3. What does `ramp(-40, -10, 4)` return? Why?
4. What does `keep_moving(3, 8, -12)` return?
5. Why can't `Settle` just check `error == 0`?
6. What's the time limit for `drive(250, 0)`?

<details>
<summary>Answers</summary>

1. 40 ÷ 4 = 10 loops, and 10 × 20 ms = 200 ms.
2. 26. The directions are opposite (30 × −30 is negative), so it's reversing, which is limited to
   one step: 30 − 4 = 26.
3. −10. Same direction and smaller, so it's slowing down, which is instant.
4. −8. 3 is less than 8, and the error is negative, so it uses −8.
5. The error is a decimal and the sensors are noisy, so it's almost never exactly 0. The move would
   never finish.
6. 1500 + 250 × 8 = 3500 ms.

</details>

## Teacher notes

- **Time:** 45 minutes.
- **Friction demo:** push a heavy book across a table with one finger. It takes a bigger push to
  *start* it moving than to *keep* it moving. That's why `keep_moving()` exists.
- **Common misunderstanding:** "TIMEOUT means the program is broken." It's the opposite: the safety
  net worked. The question is *why* the move couldn't finish.
- **`global`:** if students haven't met it yet, show a tiny example on the board of a function that
  tries to change a variable without `global`.
