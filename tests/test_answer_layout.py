import unittest

from main import _answer_window_height


class AnswerWindowLayoutTests(unittest.TestCase):
    def test_window_grows_to_fit_wrapped_answer_lines(self):
        height = _answer_window_height(
            content_lines=14,
            initial_visible_lines=5,
            line_height=20,
            initial_height=434,
            max_height=720,
        )

        self.assertEqual(614, height)

    def test_window_does_not_shrink_below_its_initial_size(self):
        height = _answer_window_height(
            content_lines=2,
            initial_visible_lines=5,
            line_height=20,
            initial_height=434,
            max_height=720,
        )

        self.assertEqual(434, height)

    def test_window_growth_is_capped_to_available_screen_space(self):
        height = _answer_window_height(
            content_lines=100,
            initial_visible_lines=5,
            line_height=20,
            initial_height=434,
            max_height=720,
        )

        self.assertEqual(720, height)


if __name__ == "__main__":
    unittest.main()
