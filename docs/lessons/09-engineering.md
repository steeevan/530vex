# Lesson 9: Thinking like a software engineer

**Big question:** Why is the whole program built this way?

**In this lesson:** no new functions. This lesson gathers the reasons behind the choices from
lessons 1 to 8, so students can use them in their own programs.

**Before this:** lessons 1 to 8.

---

## The idea

Making a program **work once** is the easy part. Software engineering is about making a program
that keeps working: when the robot gets bumped, when a new student edits it, when the battery is
low, and when someone changes it six months from now.

Here are the habits this program uses. Each one has an example from the code and the reason
behind it.

## 1. Keep the parts people change in one place

**In our code:** `SETTINGS` and `routine()` are at the top. Everything else is below
"DON'T EDIT BELOW THIS LINE."

**Why:** most changes are new moves or new numbers. Keeping them in one place means students rarely
touch the engine, and a mistake is easy to find.

## 2. Give numbers names

**In our code:** `TURN_TOLERANCE = 1.0`, not a `1.0` hidden inside `turn_to()`.

**Why:** a name explains what the number means, and changing it in one place changes it everywhere.
A bare number in the code is called a **magic number**, because nobody remembers where it came
from.

## 3. One job per function, and reuse

**In our code:** `heading_correction()` is used by `drive()`, `back_until_bumper()` and
`drive_until_distance()`. The `PID` class is used for turns, drive distance and heading.

**Why:** write it once, test it once, fix it once. If a bug is found in `heading_correction()`, one
fix repairs three moves.

## 4. Use a class when something has to remember

**In our code:** `PID` remembers the last error. `Settle` remembers when the robot entered the
window.

**Why:** a normal function forgets everything when it returns. A class bundles the memory with the
code that uses it, and you can make as many separate copies (objects) as you need, like the two PIDs
in `drive()`.

## 5. Every loop needs a way out

This is the most important rule for a robot. A loop that never ends freezes the whole routine.

| Loop in... | Stops when... | ...or gives up after |
|---|---|---|
| `turn_to()` | settled on the heading | 3 s |
| `drive()` | settled on the distance | 1.5 s + 8 ms per mm |
| `back_until_bumper()` | bumper pressed | 4 s |
| `drive_until_distance()` | 2 close readings | 4 s |
| `fire_catapult()` | motor stalls | 2 s |
| `claw_cycle()` | arm passes 145° | 2 s |
| `wait_for_inertial()` | sensor ready | 8 s |
| `wait_release()`, `wait_for_check()` | a person presses or releases a button | (a person is there) |
| the `while True` at the very end | never, on purpose: it keeps the last screen up until you press X | |

**Why:** robots get stuck. A time limit turns "frozen forever" into "one move failed, carry on."

## 6. Fail safe

**In our code:** every move brakes at the end, whether it worked or not. The whole run is inside
`try` / `except`, and `show_error()` stops all the motors **before** it shows the message.

**Why:** when something goes wrong, the safest state is "stopped." Design so that failure leads to
safety, not to a robot driving off the table.

## 7. Report problems, don't hide them

**In our code:** moves return True or False. Timeouts are counted and shown (`2 TIMEOUT(S)`,
`last: drive`). Crashes are shown on the brain screen, not only on the computer's console.

**Why:** a hidden problem is the hardest one to fix. If the robot ends in the wrong spot, the done
screen tells you *which move* had trouble. And the team once saw only "Program error, check
console" on the brain, with no computer nearby to check it. Now a crash during the run says what
went wrong, right on the robot.

## 8. Aim at fixed targets so errors don't add up

**In our code:** every heading is measured from the start (`turn_to(180)`, not "turn 90 more").

**Why:** with relative moves every small mistake piles on top of the last one. Fixed targets let each
move correct the mistakes before it (lesson 5, Part D).

## 9. Measure, don't guess

**In our code:** `programs/sensor_test.py` is a whole program just for checking the inertial
sensor. The [robot guide](../robot-guide.md) has short tests for drives, turns and the mechanisms:
put the test at the top of `routine()`, followed by `return`.

**Why:** the sensor test found that `calibrate()` gets stuck on this robot. Nobody would have
guessed that. The program was changed because of a **measurement**, not an opinion.

## 10. Change one thing at a time

**In our code:** the [robot guide](../robot-guide.md) says: change one number, test at least 3 times,
write down what happened.

**Why:** if you change three numbers and the robot gets better, you don't know which change helped.
This is the scientific method: one variable at a time, repeat the test, keep notes.

## 11. Work within your limits

**In our code:** the program is kept small, and the done and error screens show `mem free`.

**Why:** the VEX IQ brain has very little memory. A bigger version of this program crashed with
`MemoryError` while loading. That's why the explanations live in these lessons, not in long
comments in the code. Later the brain menu was taken out for the same reason: the program was close
to the limit again, and tests can go at the top of `routine()` instead. Every computer has limits.
Engineers measure them and design around them.

## 12. Prove a change didn't break anything

**In our code:** in November 2026 the program was cleaned up. Unused code was removed and a few
lines were rewritten to be clearer. Before the cleanup was saved, **both versions were run on a
pretend robot on a PC**, and every command they sent (every motor speed, every air cylinder, every
screen message) was compared. They matched exactly, apart from two lines that were deliberately
removed because they repeated something already done at the start.

**Why:** changing code without changing what it does is called **refactoring**. It's only safe if
you can prove the behavior stayed the same. Comparing old and new is one way. Testing on the real
robot is another.

**Version control helps too.** This project uses **git**. Every saved version is kept, so any
change can be undone. You can see the history on GitHub, or by typing `git log` in the VS Code
terminal.

## 13. Write for the next reader

**In our code:** names like `back_until_bumper`, `mechanism_spin` and `problem_count`. Short
comments that say *why*, not *what*.

**Why:** code is read many more times than it's written, and the next reader may be you in six
months. Compare a line from the driver program, which VEXcode blocks generated:

```python
Differential_L_Differential_L_Differential_R_Differential_R(-100, 100)
```

with the same idea in this program:

```python
mechanism_spin(-100, 100)
```

## Try it: discussion and projects

1. **Loop hunt:** find every `while` loop in `src/main.py`. For each one, what makes it stop? Check
   your answers against the table in habit 5.
2. **Spot the habit:** pick any function from lessons 2 to 8. Which of these 13 habits does it use?
3. **Break a habit on purpose (on paper):** what could happen if `drive()` had no time limit? If
   `show_error()` didn't stop the motors? If `turn_to()` used relative turns?
4. **Project ideas:**
   - Write a `drive_until_bumper_forward()` move. Which habits must it follow?
   - Make the turn test go around 3 times: `turn_to(90)`, `turn_to(180)` and so on, up to
     `turn_to(1080)` (12 turns). Compare the final error (1080 minus the `Heading` on the done
     screen) with one round. Does it grow? What does that tell you about drift?
   - Write a routine that uses a wall to reset the heading halfway through (lesson 6).

## Check your understanding

1. What is a "magic number", and how does this program avoid them?
2. Name two ways the program "fails safe."
3. Why is the `while True` loop at the very end allowed to loop forever, but `drive()` isn't?
4. What does "refactoring" mean, and how was the cleanup checked?
5. You changed `TURN_KP` and `TURN_KD` at the same time and the robot got worse. What should you do?

<details>
<summary>Answers</summary>

1. A bare number in the code with no name explaining it. This program gives every tuning number a
   name in `SETTINGS`.
2. Any two of: every move brakes at the end; `show_error()` stops the motors; time limits stop
   stuck moves.
3. That loop runs after everything else is done, so nothing is waiting for it. Its job is to keep
   the last screen up until a person presses X. A `drive()` that never ended would freeze the
   routine.
4. Changing code without changing what it does. Both versions were run on a pretend robot and every
   command they sent was compared.
5. Undo both, then change only one, test it 3 times, and write down what happened. Then try the
   other.

</details>

## Teacher notes

- **Time:** 45 minutes, best as a discussion.
- **Use it as a review.** Each habit points back to a lesson. Ask students to explain the example
  before you reveal the "why."
- **Habits 5, 6 and 7 matter most** for robotics. If time is short, focus on those.
- **For older or advanced students:** these habits have industry names: configuration separation,
  DRY ("don't repeat yourself"), timeouts and watchdogs, fail-safe design, regression testing and
  version control.
