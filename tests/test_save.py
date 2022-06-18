import unittest

import jovialengine.save as save


class TestSave(unittest.TestCase):
    def test_Save(self):
        # Act
        saves = save.Save.getAllFromFiles()
        # Assert
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].save_name, "a")
        self.assertEqual(saves[0]._mode_name, "ModeTest")
        self.assertEqual(saves[0]._mode_data, 1)
        self.assertEqual(saves[0]._shared_data, "test")


if __name__ == '__main__':
    unittest.main()
