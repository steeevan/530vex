# Lesson 8: The screen and error messages

**Big question:** How does the brain's screen tell you what happened, even when the program crashes?

**Functions in this lesson:** `show()`, `wait_release()`, `wait_for_check()`, `show_result()`,
`show_error()`, `free_memory()`, and the `try` / `except` at the end of
[`src/main.py`](../../src/main.py).

**Before this:** [Lesson 1](01-big-picture.md). The robot is helpful but not required.

---

## The idea

At a competition there's no laptop next to the robot. The brain's screen is the only way to see
what the program did.

There is no menu: when the program starts, the routine runs right away (lesson 1). So the screen
has three jobs:

1. tell you to keep your hands off while the sensor gets ready,
2. show how the routine went when it ends, and
3. show a clear message if something crashes, so you can read it **without a computer**.

| Screen | When you see it | Drawn by |
|---|---|---|
| `HANDS OFF!` | while the inertial sensor gets ready | `wait_for_inertial()` (lesson 2) |
| `INERTIAL BUSY` | the sensor took more than 8 seconds | `wait_for_inertial()` |
| `RUNNING` | while `routine()` runs | `run_routine()` (lesson 1) |
| `ROUTINE DONE` | the routine finished | `show_result()` |
| `ERROR` | something crashed | `show_error()` |

## Part A: writing on the screen

With the `MONO20` font, the brain's screen fits **6 rows of 16 letters**. "Mono" means every letter
is the same width, so 16 letters always fit, whether it's `iiii` or `WWWW`.

```python
def show(*lines):
    brain.screen.clear_screen()
    brain.screen.set_font(FontType.MONO20)
    row = 1
    for line in lines:
        brain.screen.set_cursor(row, 1)
        brain.screen.print(line[:16])
        row += 1
```

- **`*lines`** lets you pass as many lines as you like: `show("A")` or `show("A", "B", "C")`.
  Python collects them into a tuple called `lines`.
- **`line[:16]`** is a slice: it keeps only the first 16 letters, so long text can't spill over.
- It clears the screen first, then writes each line on the next row.

### Formatting numbers

The program builds its screen lines with `%`:

| Code | Meaning | Example | Result |
|---|---|---|---|
| `%d` | whole number | `"%d TIMEOUT(S)" % 2` | `2 TIMEOUT(S)` |
| `%.1f` | 1 decimal place | `"Time %.1f s" % 12.345` | `Time 12.3 s` |
| `%.1f` | 1 decimal place | `"Heading %.1f" % 89.64` | `Heading 89.6` |

## Part B: buttons

```python
def wait_release(button):
    while button.pressing():
        wait(20, MSEC)


def wait_for_check():
    wait_release(brain.buttonCheck)
    while not brain.buttonCheck.pressing():
        wait(20, MSEC)
    wait_release(brain.buttonCheck)
```

`wait_for_check()` waits for one complete press of the Check button:

1. first for any old press to end,
2. then for the button to go down,
3. then for it to come back up.

**Why wait for the button to be let go?** The loop checks the button every 20 ms. A quick tap lasts
about 100 to 200 ms, so the program would see the button "down" 5 to 10 times in a row. Waiting
for the release means **one press = one action**. This idea is called **edge detection**: you react
to the *change* from "up" to "down", not to "down" itself.

Now that there's no menu, only one screen uses the buttons: the warning in `wait_for_inertial()`
when the sensor takes too long.

```python
            show("INERTIAL BUSY", "Stop the program", "and start it", "again. Keep the",
                 "robot still.", "Check: go on")
            wait_for_check()
            return
```

The program stops here until a person reads the warning and presses Check. The best choice is
what the screen says: stop the program and start it again with the robot still.

## Part C: the done screen

When `routine()` ends, `run_routine()` (lesson 1) works out how long it took and calls
`show_result()`:

```python
    start_time = now_ms()
    routine()
    show_result((now_ms() - start_time) / 1000.0)
```

```python
def show_result(seconds):
    # The screen after the routine: time, heading, and any timeouts.
    if problem_count == 0:
        status1 = "All steps OK"
        status2 = ""
    else:
        status1 = "%d TIMEOUT(S)" % problem_count
        status2 = "last: " + last_problem
    show("ROUTINE DONE", "Time %.1f s" % seconds, "Heading %.1f" % heading_now(),
         status1, status2, "mem free:%d" % free_memory())
```

| Row | Shows | Why it's useful |
|---|---|---|
| 1 | `ROUTINE DONE` | the routine got to the end |
| 2 | `Time` | VEX IQ Autonomous Coding Skills matches last 60 seconds. Does your routine fit? |
| 3 | `Heading` | which way the robot faces at the end. The turn test in the [robot guide](../robot-guide.md) uses it. |
| 4 | `All steps OK` or `2 TIMEOUT(S)` | how many moves ran out of time (lesson 4) |
| 5 | `last: drive` (or empty) | which kind of move ran out of time last |
| 6 | `mem free` | how much memory is left (Part E) |

### The math: milliseconds to seconds

`now_ms()` counts in milliseconds. People think in seconds. 1000 ms = 1 s, so divide by 1000:

```
start_time = 2400 ms      (the routine started 2.4 s after the program)
end        = 25856 ms
time taken = 25856 − 2400 = 23456 ms
seconds    = 23456 ÷ 1000 = 23.456
"Time %.1f s" % 23.456   →   Time 23.5 s
```

`%.1f` rounds to 1 decimal place, so 23.456 shows as 23.5.

**Why `1000.0` and not `1000`?** In Python 3, `/` always gives a decimal answer anyway. Writing
`1000.0` just makes it clear to the reader that we want one.

## Part D: when something crashes

### Catching the crash: `try` / `except`

These are the last lines of the program:

```python
try:
    run_routine()
except Exception as error:
    show_error(error)

while True:              # keep the last screen up until you press X
    wait(100, MSEC)
```

If anything goes wrong while the routine runs (a typo in a name, the wrong number of arguments),
Python **raises an exception**. Without `try`, the program would die on the spot. The brain would
only show "Program error" and tell you to check the console, which is on the computer. At a
competition there's no computer, so you'd never find out what went wrong. That really happened to
the team.

With `try`, Python jumps straight to the `except` part instead. `error` holds what went wrong, and
`show_error()` puts it on the brain screen.

Then the `while True` loop does nothing, forever. It keeps the program running, so the last screen
(done or error) stays up until you press X on the brain.

### `show_error()`

```python
def show_error(error):
    # Stop the robot and show the error ON THE BRAIN SCREEN, so you can
    # read it without the console. Write down what it says.
    try:
        brake_drive()
        mechanism_stop(BRAKE)
    except Exception:
        pass
    text = repr(error)
    show("ERROR", text[0:16], text[16:32], text[32:48], text[48:64],
         "mem free:%d" % free_memory())
```

1. **Stop the motors first.** A robot that crashed in the middle of a drive could still have its
   motors running. Safety comes before the message.
2. That stop is inside its own small `try`, so even if stopping fails, the message still appears.
   `pass` means "do nothing".
3. **`repr(error)`** turns the error into text, like `TypeError(...)`.
4. The text is cut into 16-letter pieces so it fits on 4 rows.
5. The last row shows `mem free`. If the error is a `MemoryError`, that number helps.

### The math: cutting text into rows with slices

`text[a:b]` means "the letters from position `a` up to, but not including, position `b`."
Positions start at 0.

| Row | Slice | Letters |
|---|---|---|
| 2 | `text[0:16]` | 0 to 15 |
| 3 | `text[16:32]` | 16 to 31 |
| 4 | `text[32:48]` | 32 to 47 |
| 5 | `text[48:64]` | 48 to 63 |

Each slice is 16 letters long (16 − 0 = 16, 32 − 16 = 16, ...). Four rows × 16 letters = **64
letters** at most. Anything after letter 63 is cut off.

**Example:** you typed `drvie(500, 0)` instead of `drive(500, 0)`. Python can't find a function
called `drvie`. The exact words depend on the brain's Python, but the text looks something like
`NameError("name 'drvie' isn't defined")`, which is 39 letters:

| Row | Slice | What you see |
|---|---|---|
| 2 | `text[0:16]` | `NameError("name ` |
| 3 | `text[16:32]` | `'drvie' isn't de` |
| 4 | `text[32:48]` | `fined")` (only 7 letters are left) |
| 5 | `text[48:64]` | nothing |

Two things to notice:

- The cut doesn't care about words: "defined" is split over two rows.
- `text[48:64]` asks for letters that don't exist, and Python gives back empty text `""` instead
  of crashing. That's why the same line works for short and long errors.

### What `try` can't catch: errors while loading

Before the brain runs the first line of the program, Python **loads** the whole file: it reads it
and turns it into instructions. Some problems happen during loading:

- **The file is too big** for the brain's memory: `MemoryError`. An older, bigger version of this
  program once crashed like this while loading.
- **A typing mistake Python can't read at all,** like a missing `)`.

When loading fails, none of our code has run yet, not even the `try`. So the brain shows its own
"Program error" message and our ERROR screen never appears.

So if the brain says "Program error" and you never saw HANDS OFF, the program probably failed while
loading, most likely because it's too big. That's one more reason to keep the file small.

## Part E: memory left

```python
def free_memory():
    try:
        gc.collect()
        return gc.mem_free()
    except Exception:
        return -1
```

- `gc.collect()` cleans up memory the program isn't using any more ("gc" stands for "garbage
  collector").
- `gc.mem_free()` returns how many bytes are free. The done screen and the error screen show it as
  `mem free`.
- If the brain doesn't support this, it returns −1 instead of crashing.

## Why it's built this way

- **No menu, so a smaller program.** The old version had a menu with test items, and it was close
  to the brain's memory limit. Without the menu the program is smaller. Tests now go at the top of
  `routine()` for a moment (see the [robot guide](../robot-guide.md)), so they use no memory when
  you're not testing.
- **Errors show up on the brain, and the robot stops.** One `try` around the whole run catches a
  crash anywhere in it, and `show_error()` stops the motors before it shows the message.
- **The last screen stays up.** The `while True` loop at the end keeps the program running until
  you press X, so you have time to read the result or write down the error.
- **One press, one action.** Waiting for the release makes the Check button behave the way people
  expect.

## Try it

1. **Make a crash on purpose:** add `drive(600)` as the new first line of `routine()` (the heading
   is missing). Run it and read the ERROR screen. Write down what it says. Did the robot move? Then
   delete that line.
2. **Make a typo on purpose:** add `drvie(500, 0)` as the first line instead. Run it. Compare the
   ERROR screen with the table in Part D. Then delete that line.
3. **On paper:** an error's text is 50 letters long. What's on each of rows 2 to 5? Another error is
   70 letters long. Which letters don't fit?
4. **On paper:** a routine started at 1500 ms and ended at 43,280 ms. What does row 2 of the done
   screen say?

## Check your understanding

1. Why does `show_error()` stop the motors before showing the message?
2. Two moves ran out of time, and the last one was a turn. What do rows 4 and 5 of the done screen
   say?
3. Why is the whole run inside `try` / `except`?
4. Your program has a missing `)`. Will our ERROR screen show the problem? Why or why not?
5. What does `"Heading %.1f" % 359.24` give? If that was the end of the turn test, how far off was
   the robot?
6. What is the `while True` loop at the very end of the program for?
7. What does `wait_for_check()` wait for, and which screen uses it now?

<details>
<summary>Answers</summary>

1. A crash can happen in the middle of a move, with the motors still running. Stopping them comes
   first for safety.
2. `2 TIMEOUT(S)` and `last: turn`.
3. So a crash shows its error on the brain screen, instead of only "Program error" and a message
   that's only on the computer's console.
4. No. Python can't load the file, so none of our code runs, not even the `try`. The brain shows its
   own "Program error" message.
5. `Heading 359.2`. The turn test ends at 360, so it was 360 − 359.2 = 0.8° off.
6. It keeps the program running, so the last screen (done or error) stays up until you press X.
7. One full press of Check: any old press ends, then down, then up. Only the INERTIAL BUSY warning
   in `wait_for_inertial()` uses it.

**Try it 1:** `drive(600)` crashes the moment it's called, before the robot moves, because Python
checks the number of arguments first. You get a `TypeError`.
**Try it 3:** 50 letters: row 2 = letters 0 to 15, row 3 = 16 to 31, row 4 = 32 to 47, row 5 =
48 and 49 (only 2 letters). 70 letters: letters 64 to 69 (6 letters) don't fit.
**Try it 4:** 43280 − 1500 = 41780 ms = 41.78 s, so `Time 41.8 s`.

</details>

## Teacher notes

- **Time:** 40 minutes. A good lesson for days without the robot (Try it 3 and 4 work on paper).
- **Not tested on the real robot yet:** this way of starting (no menu, errors shown on the brain)
  has only been run on a pretend robot on a PC. If the real brain shows something different,
  that's worth writing down and discussing.
- **`try` / `except` is a big idea.** Compare it to a safety net under a trapeze: it doesn't stop
  the fall, it catches it. Then make the difference clear between errors while **running** (caught,
  shown on our ERROR screen) and errors while **loading** (not caught, the brain's own "Program
  error").
- **Try it 1 is safe:** `drive(600)` fails before any motor moves. Still keep hands clear, since
  the robot is "live" once the program starts.
- **Edge detection** shows up everywhere: keyboards, game controllers, door bells. Ask for more
  examples.
- **Watch `mem free`** whenever students add code, and compare the number before and after.
