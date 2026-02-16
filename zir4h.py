#!/usr/bin/env python3
"""
Zir4h - A terminal 9-ball table game for Termux.
Run: python3 zir4h.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

TABLE_W = 72.0
TABLE_H = 36.0
FRICTION = 0.985
MIN_SPEED = 0.03
MAX_STEPS = 2200
BALL_R = 1.1
POCKET_R = 2.3

POCKETS = [
    (0.0, 0.0),
    (TABLE_W / 2, 0.0),
    (TABLE_W, 0.0),
    (0.0, TABLE_H),
    (TABLE_W / 2, TABLE_H),
    (TABLE_W, TABLE_H),
]


@dataclass
class Ball:
    number: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    pocketed: bool = False

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)


class Zir4hGame:
    def __init__(self) -> None:
        self.players = ["Player 1", "Player 2"]
        self.turn = 0
        self.balls = self._rack_balls()
        self.winner: int | None = None

    def _rack_balls(self) -> dict[int, Ball]:
        cue = Ball(0, TABLE_W * 0.22, TABLE_H / 2)

        head_x = TABLE_W * 0.72
        head_y = TABLE_H / 2
        spacing = BALL_R * 2.08
        triangle = [
            (0, 0),
            (1, -0.5), (1, 0.5),
            (2, -1), (2, 0), (2, 1),
            (3, -1.5), (3, -0.5), (3, 0.5), (3, 1.5),
        ]

        # Position slots for balls 1..9 (10 slots with one empty)
        random_slots = triangle[1:]
        random.shuffle(random_slots)

        balls = {0: cue}
        balls[1] = Ball(1, head_x + triangle[0][0] * spacing, head_y + triangle[0][1] * spacing)
        balls[9] = Ball(9, head_x + triangle[2][0] * spacing, head_y + triangle[2][1] * spacing)

        nums = [2, 3, 4, 5, 6, 7, 8]
        for num, slot in zip(nums, random_slots):
            row, off = slot
            balls[num] = Ball(num, head_x + row * spacing, head_y + off * spacing)

        return balls

    def draw(self) -> str:
        grid_w = 72
        grid_h = 20
        board = [[" " for _ in range(grid_w)] for _ in range(grid_h)]

        for px, py in POCKETS:
            gx, gy = self._to_grid(px, py, grid_w, grid_h)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    x = min(max(gx + dx, 0), grid_w - 1)
                    y = min(max(gy + dy, 0), grid_h - 1)
                    board[y][x] = "O"

        for n in sorted(self.balls):
            b = self.balls[n]
            if b.pocketed:
                continue
            gx, gy = self._to_grid(b.x, b.y, grid_w, grid_h)
            mark = "C" if n == 0 else str(n)
            board[gy][gx] = mark[-1]

        top = "+" + "-" * grid_w + "+"
        lines = [top]
        for row in board:
            lines.append("|" + "".join(row) + "|")
        lines.append(top)
        return "\n".join(lines)

    @staticmethod
    def _to_grid(x: float, y: float, gw: int, gh: int) -> tuple[int, int]:
        gx = int((x / TABLE_W) * (gw - 1))
        gy = int((y / TABLE_H) * (gh - 1))
        return min(max(gx, 0), gw - 1), min(max(gy, 0), gh - 1)

    def lowest_ball(self) -> int:
        active = [n for n, b in self.balls.items() if n != 0 and not b.pocketed]
        return min(active)

    def shot(self, angle_deg: float, power: float) -> tuple[list[int], int | None, bool]:
        cue = self.balls[0]
        rad = math.radians(angle_deg)
        speed = max(0.4, min(power, 100.0)) / 6.5
        cue.vx = math.cos(rad) * speed
        cue.vy = math.sin(rad) * speed

        pocketed: list[int] = []
        first_hit: int | None = None
        for _ in range(MAX_STEPS):
            moving = False
            # Move
            for b in self.balls.values():
                if b.pocketed:
                    continue
                if abs(b.vx) > MIN_SPEED or abs(b.vy) > MIN_SPEED:
                    moving = True
                b.x += b.vx
                b.y += b.vy
                b.vx *= FRICTION
                b.vy *= FRICTION

                # Cushion bounce
                if b.x <= BALL_R:
                    b.x = BALL_R
                    b.vx = abs(b.vx)
                elif b.x >= TABLE_W - BALL_R:
                    b.x = TABLE_W - BALL_R
                    b.vx = -abs(b.vx)
                if b.y <= BALL_R:
                    b.y = BALL_R
                    b.vy = abs(b.vy)
                elif b.y >= TABLE_H - BALL_R:
                    b.y = TABLE_H - BALL_R
                    b.vy = -abs(b.vy)

                # Pockets
                if self._is_in_pocket(b):
                    b.pocketed = True
                    b.vx = b.vy = 0.0
                    if b.number not in pocketed:
                        pocketed.append(b.number)

            # Collisions
            live = [b for b in self.balls.values() if not b.pocketed]
            for i in range(len(live)):
                for j in range(i + 1, len(live)):
                    a, c = live[i], live[j]
                    dx = c.x - a.x
                    dy = c.y - a.y
                    dist = math.hypot(dx, dy)
                    if dist == 0 or dist > BALL_R * 2:
                        continue

                    nx, ny = dx / dist, dy / dist
                    overlap = BALL_R * 2 - dist
                    a.x -= nx * overlap / 2
                    a.y -= ny * overlap / 2
                    c.x += nx * overlap / 2
                    c.y += ny * overlap / 2

                    rel = (a.vx - c.vx) * nx + (a.vy - c.vy) * ny
                    if rel <= 0:
                        continue

                    impulse = rel
                    a.vx -= impulse * nx
                    a.vy -= impulse * ny
                    c.vx += impulse * nx
                    c.vy += impulse * ny

                    if first_hit is None:
                        if a.number == 0 and c.number != 0:
                            first_hit = c.number
                        elif c.number == 0 and a.number != 0:
                            first_hit = a.number

            if not moving:
                break

        foul = False
        if 0 in pocketed:
            foul = True
            self._respawn_cue_ball()

        required = self.lowest_ball() if not self.balls[9].pocketed else 9
        if first_hit is None or first_hit != required:
            foul = True

        return pocketed, first_hit, foul

    def _respawn_cue_ball(self) -> None:
        cue = self.balls[0]
        cue.pocketed = False
        cue.vx = cue.vy = 0.0
        cue.x, cue.y = TABLE_W * 0.2, TABLE_H / 2

    @staticmethod
    def _is_in_pocket(ball: Ball) -> bool:
        for px, py in POCKETS:
            if math.hypot(ball.x - px, ball.y - py) <= POCKET_R:
                return True
        return False

    def remaining(self) -> list[int]:
        return [n for n in range(1, 10) if not self.balls[n].pocketed]

    def run(self) -> None:
        print("=" * 74)
        print("Zir4h - 9 Ball for Termux")
        print("Pot the 9-ball legally by hitting the lowest-numbered ball first.")
        print("Controls per shot: angle(0-359) power(1-100).")
        print("=" * 74)

        while self.winner is None:
            print("\n" + self.draw())
            player = self.players[self.turn]
            target = self.lowest_ball()
            print(f"\n{player}'s turn | Required first contact: {target}")
            print(f"Remaining balls: {self.remaining()}")

            angle = self._ask_float("Angle (0-359): ", 0, 359)
            power = self._ask_float("Power (1-100): ", 1, 100)

            pocketed, first_hit, foul = self.shot(angle, power)

            if first_hit is None:
                print("No object ball was hit.")
            else:
                print(f"First ball hit: {first_hit}")

            if pocketed:
                print("Pocketed this shot:", sorted(pocketed))
            else:
                print("No balls pocketed.")

            legal_nine = 9 in pocketed and not foul
            illegal_nine = 9 in pocketed and foul

            if legal_nine:
                self.winner = self.turn
                print(f"\n{player} pots the 9-ball legally and wins! 🎱")
                break
            if illegal_nine:
                print("9-ball was pocketed on a foul. Spotting the 9-ball back on table.")
                self._spot_nine_ball()

            if foul:
                print("FOUL! Turn passes.")
                self.turn = 1 - self.turn
            else:
                scored = any(n in pocketed for n in range(1, 10))
                if scored:
                    print("Nice shot! You keep the table.")
                else:
                    self.turn = 1 - self.turn

    def _spot_nine_ball(self) -> None:
        nine = self.balls[9]
        nine.pocketed = False
        nine.vx = nine.vy = 0.0
        nine.x, nine.y = TABLE_W * 0.72, TABLE_H / 2

    @staticmethod
    def _ask_float(prompt: str, lo: float, hi: float) -> float:
        while True:
            raw = input(prompt).strip()
            try:
                value = float(raw)
            except ValueError:
                print("Enter a number.")
                continue
            if lo <= value <= hi:
                return value
            print(f"Enter a value between {lo} and {hi}.")


if __name__ == "__main__":
    try:
        Zir4hGame().run()
    except KeyboardInterrupt:
        print("\nGame ended.")
