# Zir4h 🎱

A terminal-friendly **9-ball pool game** built for **Termux**.

## Install + Run on Termux

```bash
pkg update -y
pkg install python git -y
git clone https://github.com/<your-username>/Zir4h.git
cd Zir4h
python3 zir4h.py
```

## Why `zir4h.py: command not found` happens

In Termux, typing only `zir4h.py` usually fails because the current folder is not on `PATH`.
Use one of these instead:

```bash
python3 zir4h.py
```

or make it executable and run with `./`:

```bash
chmod +x zir4h.py
./zir4h.py
```

## How to play

- Two-player local turns (`Player 1` / `Player 2`)
- On each shot, enter:
  - `Angle` (0-359)
  - `Power` (1-100)
- You must hit the **lowest-numbered ball first**.
- Pocket the **9-ball legally** to win.
- If you foul, turn passes.

Enjoy playing **Zir4h** in your terminal.
