# Lesson 8: The screen and the menu

**Big question:** How do the buttons, the screen and the error messages work?

**Functions in this lesson:** `show()`, `show_row()`, `wait_release()`, `wait_for_check()`,
`show_result()`, `show_error()`, `free_memory()`, the `item_...()` functions, `MENU`, `run_item()`,
`draw_menu()`, `menu()` in [`src/main.py`](../../src/main.py).

**Before this:** [Lesson 1](01-big-picture.md). The robot is helpful but not required.

---

## The idea

At a competition there's no laptop next to the robot. The brain's screen and its buttons (Left,
Right, Check) are the only way to talk to the program. So the program has a small menu: pick the
routine or a test, see the result, and see a clear message if something crashes.

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

```python
def show_row(row, text):
    brain.screen.set_cursor(row, 1)
    brain.screen.print(("%-16s" % text)[:16])
```

`show_row()` rewrites **one** row without clearing the whole screen. That's used for live numbers,
because clearing the screen 10 times a second would make it flicker.

**Why `"%-16s"`?** It pads the text with spaces up to 16 letters. Printing on top of old text
doesn't erase it. Say the row said `Turn test` and you print `Claw` over it:

| Printed | What you see |
|---|---|
| `Claw` | `Claw test` (the old letters are still there) |
| `"%-16s" % "Claw"` | `Claw` followed by 12 spaces, which erase the old letters |

### Formatting numbers

| Code | Meaning | Example | Result |
|---|---|---|---|
| `%d` | whole number | `"%d TIMEOUT(S)" % 2` | `2 TIMEOUT(S)` |
| `%.1f` | 1 decimal place | `"Time %.1f s" % 12.345` | `Time 12.3 s` |
| `%8.1f` | 1 decimal, at least 8 wide | `"%8.1f deg" % 5` | `     5.0 deg` |
| `%-16s` | text, padded on the right to 16 | `"%-16s" % "Hi"` | `Hi` + 14 spaces |

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

**Why wait for the button to be let go?** The menu checks the buttons every 20 ms. A quick tap lasts
about 100 to 200 ms. Without `wait_release()`, the menu would see the button held down for 5 to 10
checks in a row, and one tap would skip 5 to 10 items. Waiting for the release means
**one press = one action**. This idea is called **edge detection**: you react to the *change* from
"up" to "down", not to "down" itself.

`wait_for_check()` waits for one complete press: first for any old press to end, then for the
button to go down, then for it to come back up.

## Part C: the menu is a list

```python
MENU = [
    ("Routine", item_routine),
    ("Show heading", item_show_heading),
    ("Turn test", item_turn_test),
    ("Drive test", item_drive_test),
    ("Catapult", item_catapult),
    ("Claw", item_claw),
]
```

Each item is a **pair**: the name to show, and the function to run.

Notice `item_routine` has **no brackets**. `item_routine()` would *run* the function. `item_routine`
on its own *is* the function, like writing down a recipe's name without cooking it yet. Python lets
you keep functions in a list and call them later.

- `MENU[2]` is `("Turn test", item_turn_test)`
- `MENU[2][0]` is `"Turn test"`
- `MENU[2][1]` is the function `item_turn_test`

```python
def menu():
    index = 0
    draw_menu(index)
    while True:
        if brain.buttonLeft.pressing():
            index = (index - 1) % len(MENU)
            draw_menu(index)
            wait_release(brain.buttonLeft)
        elif brain.buttonRight.pressing():
            index = (index + 1) % len(MENU)
            draw_menu(index)
            wait_release(brain.buttonRight)
        elif brain.buttonCheck.pressing():
            wait_release(brain.buttonCheck)
            try:
                run_item(index)
            except Exception as error:
                show_error(MENU[index][0], error)
            draw_menu(index)
        wait(20, MSEC)
```

`menu()` loops forever (`while True`). That's on purpose: it's the one loop in the program that
should never end.

### The math: wrapping around with `%`

There are 6 items, numbered 0 to 5. Pressing Right on the last item should go back to the first,
and pressing Left on the first should go to the last.

| index | Right: (index + 1) % 6 | Left: (index − 1) % 6 |
|---|---|---|
| 0 | 1 | −1 % 6 = **5** |
| 3 | 4 | 2 |
| 5 | 6 % 6 = **0** | 4 |

It's the same modulo "clock math" as `angle_diff()` in lesson 2.

### Running an item

```python
def run_item(index):
    name = MENU[index][0]
    action = MENU[index][1]
    reset_problems()
    brain_inertial.set_rotation(0, DEGREES)    # 0 = the way the robot faces now
    show("RUNNING", name)
    action()
```

1. Look up the name and the function.
2. Reset the timeout count (lesson 4).
3. **Set the heading to 0.** Whichever way the robot faces when you press Check becomes 0 for this
   run. That's why you line the robot up *before* pressing Check.
4. Show "RUNNING", then run the function.

The menu waits for you to **let go** of Check before it starts, so your hand is off the robot when
it moves.

```python
def draw_menu(index):
    show("AUTO MENU %d/%d" % (index + 1, len(MENU)),
         "mem free:%d" % free_memory(),
         "< " + MENU[index][0] + " >",
         "",
         "Left/Right:pick",
         "Check: run")
```

It shows `index + 1` because people count from 1, while Python counts from 0.

## Part D: when something crashes

`menu()` runs each item inside `try` / `except`. If anything goes wrong (a typo in `routine()`, a
wrong number of arguments), Python **raises an exception**. Instead of the program dying, the
`except` part catches it and calls `show_error()`:

```python
def show_error(where, error):
    # Stop the robot, then keep the error on screen until Check is pressed.
    try:
        brake_drive()
        mechanism_stop(BRAKE)
    except Exception:
        pass
    text = repr(error)
    show("ERROR", where, text[0:16], text[16:32], text[32:48], "Check: menu")
    wait_for_check()
```

1. **Stop the motors first.** A robot that crashed in the middle of a drive could still have its
   motors running. Safety comes before the message.
2. **`repr(error)`** turns the error into text, like `TypeError(...)`.
3. The text is cut into 16-letter pieces (`[0:16]`, `[16:32]`, `[32:48]`) so it fits on 3 rows.
4. The message stays until you press Check, then you're back at the menu. You don't have to restart
   the program.

## Part E: the menu items

```python
def item_routine():
    start_time = now_ms()
    routine()
    seconds = (now_ms() - start_time) / 1000.0
    show_result("ROUTINE DONE", "Time %.1f s" % seconds)
```

It runs your routine and times it. VEX IQ Autonomous Coding Skills matches last 60 seconds, so the
time tells you whether your routine fits.

| Item | What it does | Lesson |
|---|---|---|
| `item_show_heading()` | Shows the heading live, 10 times a second, until you press Check | 2 |
| `item_turn_test()` | Turns to 90, 180, 270, 360, then shows how far off it ended | 5 |
| `item_drive_test()` | Drives 500 mm so you can measure it | 2 |
| `item_catapult()` | Fires the catapult once | 7 |
| `item_claw()` | Opens the claw, then does one claw cycle | 7 |

They all end with `show_result()`:

```python
def show_result(title, line2="", line3=""):
    if problem_count == 0:
        status1 = "All steps OK"
        status2 = ""
    else:
        status1 = "%d TIMEOUT(S)" % problem_count
        status2 = "last: " + last_problem
    show(title, line2, line3, status1, status2, "Check: menu")
    wait_for_check()
```

`line2=""` and `line3=""` are **default values**: if you don't pass them, they're empty.

### Memory left

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
- `gc.mem_free()` returns how many bytes are free. The menu shows it as `mem free`.
- If the brain doesn't support this, it returns −1 instead of crashing.

## Why it's built this way

- **Test tools are part of the program.** You can check the heading, turns, drives and mechanisms
  without downloading anything new, which matters at a competition.
- **Errors stay visible and the robot stops.** A crash shows what went wrong and stops the motors.
- **The menu is data.** Adding an item means adding one line to `MENU`. The loop never changes.
- **One press, one action.** Waiting for the release makes the buttons behave the way people expect.

## Try it

1. **Add your own menu item.** Above `MENU`, write:

   ```python
   def item_there_and_back():
       drive(300, 0)
       drive(-300, 0)
       show_result("THERE AND BACK", "Measure it!")
   ```

   Then add `("There and back", item_there_and_back),` to `MENU`. The function has to be defined
   **above** `MENU`, because the list is built when Python reaches it. Check `mem free` before and
   after.
2. **Make a crash on purpose:** in `routine()`, write `drive(600)` (the heading is missing). Run it
   and read the error screen. Then fix it.
3. **On paper:** with 7 menu items, what's `(0 - 1) % 7`? And `(6 + 1) % 7`?

## Check your understanding

1. What would happen in the menu without `wait_release()`?
2. What is `MENU[4][0]`? What is `MENU[4][1]`?
3. Why does `show_error()` stop the motors before showing the message?
4. What does `"%-16s" % "Claw"` give?
5. Why does `run_item()` set the rotation to 0?

<details>
<summary>Answers</summary>

1. One tap would be seen many times, so the menu would skip several items, or run an item again
   right after it finished.
2. `"Catapult"`, and the function `item_catapult`.
3. A crash can happen in the middle of a move, with the motors still running. Stopping them comes
   first for safety.
4. `"Claw"` followed by 12 spaces (16 letters in total).
5. So the way the robot faces when you press Check becomes heading 0 for that run.

**Try it 3:** 6 and 0.

</details>

## Teacher notes

- **Time:** 40 minutes. A good lesson for days without the robot (Try it 2 and 3 work on paper).
- **Functions as values** (Part C) is a big idea. Ask students to explain the difference between
  `item_claw` and `item_claw()`.
- **Edge detection** shows up everywhere: keyboards, game controllers, door bells. Ask for more
  examples.
- **Adding a menu item** (Try it 1) is a safe first change below the "DON'T EDIT" line. Supervise
  it, and watch `mem free`.
