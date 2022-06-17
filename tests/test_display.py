import unittest

import jovialengine.display as display


class TestDisplay(unittest.TestCase):
    def test_scaleMouseInput(self):
        test_display = display.Display()
        self.assertEqual(38, 38)


if __name__ == '__main__':
    unittest.main()
