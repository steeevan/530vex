# Lesson 7: The claw and the catapult

**Big question:** How do two motors run two different mechanisms?

**Functions in this lesson:** `mechanism_spin()`, `mechanism_stop()`, `claw_open()`,
`claw_close()`, `set_catapult_level()`, `start_mechanisms()`, `fire_catapult()`, `claw_cycle()` in
[`src/main.py`](../../src/main.py).

**Before this:** [Lesson 4](04-smooth-and-done.md) (time limits). Lessons 5 and 6 aren't needed
for this one.

> **Safety first:** the catapult can fire whenever these functions run, including at the start of
> `routine()`. Keep hands and faces away from it, and don't load a game piece until you mean to fire.

---

## The idea

The robot has two mechanism motors, `C_L` (port 4) and `C_R` (port 10). The builders connected them
so that **both motors work on both mechanisms**:

- spin them the **same way** and the **claw arm** moves;
- spin them **opposite ways** and the **catapult** moves.

It's a clever build trick: two motors can do two jobs. The cost is that **the robot can only do one
of those jobs at a time.**

The robot also uses **air** (pneumatics). One pneumatic module in port 9 controls two cylinders:

| Cylinder | Extend | Retract |
|---|---|---|
| `CYLINDER1` (claw) | close the claw (grab) | open the claw |
| `CYLINDER2` (catapult level) | level 4 | level 3 |

## Part A: the motor helpers

```python
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
```

What each pair of numbers does, from the code:

| `mechanism_spin(...)` | What moves |
|---|---|
| `(-100, -100)` | the claw arm flips over |
| `(75, 75)` | the claw arm swings back |
| `(-100, 100)` | the catapult releases (fires) |
| `(100, -100)` | the catapult winds back down |

`mechanism_stop(BRAKE)` holds the motors still. `mechanism_stop(COAST)` lets them turn freely.

## Part B: air

```python
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
```

- **Air isn't instant.** It takes time to fill a cylinder. `claw_close()` waits `CLAW_GRIP_MS`
  (200 ms) so the claw has really closed before anything else happens.
- After `set_catapult_level()`, wait about 300 ms before firing, for the same reason.
- `set_catapult_level()` ignores any number that isn't 3 or 4. A typo like `set_catapult_level(5)`
  does nothing instead of doing something strange.

## Part C: `fire_catapult()`

```python
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
```

### The timeline

| Time | What happens |
|---|---|
| 0 to 250 ms | spin to **release**: the catapult fires |
| 250 to 950 ms | spin the other way to **wind it down**, without checking anything yet |
| from 950 ms | keep winding, and check every 20 ms: has the motor stopped? |
| when stopped (or 2 more seconds have passed) | **brake** to hold the catapult down |

### Using the motor as a sensor

How does the program know the catapult is fully wound? There's no sensor on it. Instead:
**when the catapult reaches the end, it can't move any further, so the motor stalls.** The motor's
speed drops to almost 0. When `C_R`'s speed is below `CATAPULT_STOPPED_BELOW` (5%), the catapult
must be all the way down.

### Why wait 700 ms before checking?

A motor that's just **starting** is also going slowly, close to 0%. If the program checked right
away, it would think "stopped, done!" before the catapult had even moved. Waiting 700 ms first
makes sure the motor is up to speed. After that, a slow motor really means "it hit the end."

### The time limit

If the motor never slows down (say a gear slips and it spins freely), the loop would run forever.
After `CATAPULT_STALL_TIMEOUT_MS` (2 seconds) it gives up, brakes and reports `catapult`.

## Part D: `claw_cycle()`

```python
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
```

1. **Grab:** close the claw and wait 200 ms.
2. **Flip:** spin both motors at −100%. `set_position(0)` starts counting the arm's angle from
   here.
3. **Watch the angle:** keep going until the arm has turned more than `CLAW_ARM_DEGREES` (145°), or
   2 seconds have passed.
4. **Let go:** open the claw and wait 50 ms.
5. **Swing back:** spin at 75% for 500 ms.
6. **Relax:** stop in `COAST` so the arm can settle.

**Two ways of deciding "far enough":**
- The flip is measured by **angle** (145°), because it has to stop in the right place to drop the
  game piece.
- The swing back is measured by **time** (500 ms), because it only has to get out of the way.

## Part E: getting ready at the start

```python
def start_mechanisms():
    # Like the driver program at start-up. Arming FIRES the catapult once,
    # so load no game piece first. (No pump_on(): the driver never calls it.
    # If the cylinders don't move, add pneumatic_9.pump_on() here.)
    claw_open()
    set_catapult_level(3)
    return fire_catapult()
```

This does what the driver program does when it starts: open the claw, set level 3, and arm the
catapult. Arming runs `fire_catapult()`, so **the catapult fires once**. That's why you load nothing
before it.

## Why it's built this way

- **Copy what already works.** All the timings (250 ms, 700 ms, 145°, 75%...) come from the driver
  program, which the team has already used on the real robot. Don't invent new numbers when tested
  ones exist.
- **Then add what autonomous needs.** The driver program waits for the catapult like this:

  ```python
  while not math.fabs(C_R.velocity(PERCENT)) < 5:
      wait(20, MSEC)
  ```

  There's no time limit. While you drive, a person can see a problem and stop the robot. During
  autonomous nobody can help, so this program adds a time limit to every wait.
- **Say it simply.** `not (speed < 5)` means the same as `speed >= 5`. The new code uses the simpler
  version, because double negatives are easy to misread.
- **Give things good names.** The driver program was made with VEXcode blocks, which turned a custom
  block into this function call:

  ```python
  Differential_L_Differential_L_Differential_R_Differential_R(-100, 100)
  ```

  This program calls the same thing `mechanism_spin(-100, 100)`.
- **One thing at a time makes sharing safe.** In the driver program the claw and catapult code run
  at the same time, so the claw has to wait for the catapult to finish (`while not tan_she == 0`).
  In autonomous, one move finishes before the next starts, so they can't clash.

## Try it

1. Run **Catapult** from the menu. Film it in slow motion on a phone. Can you see the release, the
   wind-down and the stop? Do they match the timeline?
2. Run **Claw** from the menu. Watch where the arm stops. What do you think would happen with
   `CLAW_ARM_DEGREES = 120`? (Try it carefully, then put it back to 145.)
3. **On paper:** what's the longest `fire_catapult()` can take before it gives up?
4. **Think:** what would happen if you removed the 700 ms wait and checked for a stall straight
   away?

## Check your understanding

1. Which way do the two motors spin to fire the catapult? To flip the claw?
2. Why does `fire_catapult()` wait 700 ms before checking for a stall?
3. What does `CATAPULT_STALL_TIMEOUT_MS` protect against?
4. Why can't the robot fire the catapult and flip the claw at the same time?
5. Why does `claw_close()` wait 200 ms?

<details>
<summary>Answers</summary>

1. Catapult: opposite ways, `(-100, 100)` to release and `(100, -100)` to wind down. Claw:
   the same way, `(-100, -100)`.
2. A motor that's just starting is also slow. Without the wait it would look "stalled" right away.
3. A motor that never stalls (say, a slipping gear). Without it the loop would never end.
4. Both mechanisms use the same two motors.
5. Air takes time to move the cylinder, so the claw needs time to really close.

**Try it 3:** 250 + 700 + 2000 = 2950 ms, plus up to one more 20 ms check.
**Try it 4:** the motor would still be starting up and slow, so the program would think the
catapult was already wound and brake almost at once.

</details>

## Teacher notes

- **Time:** 40 minutes.
- **Safety:** go over the catapult rules before anyone runs anything. `start_mechanisms()` fires it.
- **Show the build:** take the robot and show students how both motors connect to both mechanisms.
  The code makes much more sense once they see the gears.
- **"Motor as a sensor"** is a powerful idea. Ask what else could be detected this way (for example,
  the robot pushing against a wall, because the drive motors slow down).
- **Check the air:** if the cylinders don't move, the air may need pumping. The comment in
  `start_mechanisms()` says where `pump_on()` would go.
