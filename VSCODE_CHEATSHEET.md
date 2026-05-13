# VS Code keyboard cheat-sheet for Lab 5

Shortcuts below are for **Windows / Linux**. On macOS, replace `Ctrl`
with `Cmd` and `Alt` with `Option` (except for a few — noted inline).

Aim to use the keyboard for everything you do at least once during the
lab. The first hour feels slower; after that you will navigate code
faster than you ever did with the mouse.

---

## 1. Moving around the file tree

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Open file by name (fuzzy search)                | `Ctrl+P`             |
| Open the Explorer side bar                      | `Ctrl+Shift+E`       |
| Toggle the side bar                             | `Ctrl+B`             |
| Switch between editor and side bar              | `Ctrl+0` / `Ctrl+1`  |
| Reveal current file in the Explorer             | `Ctrl+Shift+P` → "Reveal Active File" |
| Open a recently used file                       | `Ctrl+P` then `Ctrl+Tab` |

**Tip:** in the `Ctrl+P` box you can append `:42` to jump to line 42 of
the chosen file, or `@symbol` to jump to a symbol.

## 2. Moving around the code

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Go to symbol in **this file**                   | `Ctrl+Shift+O`       |
| Go to symbol in **the whole workspace**         | `Ctrl+T`             |
| Go to definition                                | `F12`                |
| Peek definition (inline)                        | `Alt+F12`            |
| Find all references                             | `Shift+F12`          |
| Go back / forward (like a browser)              | `Alt+Left` / `Alt+Right` |
| Go to line number                               | `Ctrl+G`             |
| Go to bracket match                             | `Ctrl+Shift+\`       |
| Jump to next / previous problem (error)         | `F8` / `Shift+F8`    |

## 3. Search

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Find in current file                            | `Ctrl+F`             |
| Replace in current file                         | `Ctrl+H`             |
| Find across **all files**                       | `Ctrl+Shift+F`       |
| Replace across all files                        | `Ctrl+Shift+H`       |
| Toggle case sensitivity / whole word / regex    | `Alt+C` / `Alt+W` / `Alt+R` |
| Open Command Palette (do anything by name)      | `Ctrl+Shift+P`       |

Tick the regex (`.*`) button to use patterns like `def borrow_\w+\(`
when you are hunting for a family of functions.

## 4. Editing efficiently

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Duplicate the current line                      | `Shift+Alt+Down/Up`  |
| Move line up / down                             | `Alt+Up` / `Alt+Down`|
| Delete the current line                         | `Ctrl+Shift+K`       |
| Comment / uncomment line                        | `Ctrl+/`             |
| Comment block                                   | `Shift+Alt+A`        |
| Select next occurrence of word                  | `Ctrl+D`             |
| Select **all** occurrences in file              | `Ctrl+Shift+L`       |
| Add cursor above / below                        | `Ctrl+Alt+Up/Down`   |
| Format document (Black, Prettier, ...)          | `Shift+Alt+F`        |
| Rename symbol (refactor across files)           | `F2`                 |
| Trigger IntelliSense suggestion                 | `Ctrl+Space`         |
| Trigger parameter hints                         | `Ctrl+Shift+Space`   |

**Multi-cursor is the superpower most students miss.** `Ctrl+D` keeps
adding cursors at the next match of the word under the cursor — perfect
for renaming a local variable in 5 places at once.

## 5. Working with multiple files

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Switch between open tabs                        | `Ctrl+Tab` (hold)    |
| Close current tab                               | `Ctrl+W`             |
| Reopen closed tab                               | `Ctrl+Shift+T`       |
| Split editor right                              | `Ctrl+\`             |
| Focus editor group 1 / 2 / 3                    | `Ctrl+1` / `Ctrl+2` / `Ctrl+3` |
| Move editor between groups                      | `Ctrl+Alt+Right/Left`|

## 6. Terminal & tasks

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Toggle integrated terminal                      | `` Ctrl+`  ``        |
| New terminal                                    | `` Ctrl+Shift+`  ``  |
| Kill terminal                                   | Terminal trash icon  |
| Run last task                                   | `Ctrl+Shift+P` → "Tasks: Run Task" |
| Move focus between editor and terminal          | `` Ctrl+`  `` (toggles) |

## 7. Debugging Python

Use `Run and Debug` (left bar) or the keys below. Make sure the
**Python** extension is installed.

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Start / continue                                | `F5`                 |
| Run without debugging                           | `Ctrl+F5`            |
| Toggle breakpoint                               | `F9`                 |
| Step over / into / out                          | `F10` / `F11` / `Shift+F11` |
| Stop debugging                                  | `Shift+F5`           |
| Open Debug console                              | `Ctrl+Shift+Y`       |

Tip: set a breakpoint inside `return_book` (Bug 1) and click "Return" on
an overdue loan in the running app to inspect `raw_days` and
`days_overdue` live.

## 8. Git inside VS Code

| Action                                          | Shortcut             |
| ----------------------------------------------- | -------------------- |
| Open Source Control view                        | `Ctrl+Shift+G`       |
| Stage current change                            | `+` icon next to file in the SCM view |
| Show inline blame (with GitLens extension)      | hover the line       |
| Open the file's history (GitLens)               | right-click → "Open File History" |
| Diff working file vs. HEAD                      | Click the file in SCM view |

## 9. Pytest from inside VS Code

1. Install the **Python** and **Python Test Explorer** extensions.
2. `Ctrl+Shift+P` → "Python: Configure Tests" → choose `pytest` → choose
   the `tests` directory.
3. Use the beaker icon in the left bar to:
   - run / debug individual tests with one click,
   - re-run only failed tests (the curved arrow icon),
   - jump from a failing test directly to the failing line.

## 10. Recommended extensions

Install these once and reuse them for the rest of the semester:

- **Python** (Microsoft)
- **Pylance** (better IntelliSense)
- **Jinja** (template syntax highlighting)
- **GitLens** (inline blame, history)
- **SQLite Viewer** (open `library.db` directly in the editor)
- **autoDocstring** (generate Python docstrings)
- **Even Better TOML** / **YAML** if you start touching config files

## 11. Practice path for Lab 5

If you only memorize five shortcuts today, make them these:

1. **`Ctrl+P`** — open any file in two seconds.
2. **`Ctrl+Shift+F`** — search every file in the project.
3. **`F12`** — jump to where a function is defined.
4. **`Shift+F12`** — find every place a function is called.
5. **`F2`** — rename a symbol everywhere safely.

Everything else in this cheat-sheet will come naturally as you keep
working in VS Code.
