import unittest

from zir4h import TABLE_H, TABLE_W, Zir4hGame


class Zir4hTests(unittest.TestCase):
    def test_rack_contains_all_balls(self):
        game = Zir4hGame()
        self.assertEqual(set(game.balls.keys()), set(range(10)))

    def test_rack_has_one_apex_and_nine_center(self):
        game = Zir4hGame()
        one = game.balls[1]
        nine = game.balls[9]
        self.assertLess(nine.x, game.balls[8].x + 20)  # sanity check ball exists near rack zone
        self.assertGreaterEqual(nine.x, one.x)

    def test_foul_evaluation_uses_required_contact(self):
        game = Zir4hGame()
        # Legal first hit on required ball, and cue is not pocketed.
        foul = game._evaluate_foul(first_hit=1, pocketed=[1], required=1)
        self.assertFalse(foul)

    def test_cue_pocket_is_foul(self):
        game = Zir4hGame()
        foul = game._evaluate_foul(first_hit=1, pocketed=[0, 1], required=1)
        self.assertTrue(foul)

    def test_single_shot_executes(self):
        game = Zir4hGame()
        pocketed, first_hit, foul = game.shot(0, 40)
        self.assertIsInstance(pocketed, list)
        self.assertTrue(first_hit is None or 1 <= first_hit <= 9)
        self.assertIsInstance(foul, bool)
        cue = game.balls[0]
        self.assertTrue(0 <= cue.x <= TABLE_W)
        self.assertTrue(0 <= cue.y <= TABLE_H)


if __name__ == "__main__":
    unittest.main()
