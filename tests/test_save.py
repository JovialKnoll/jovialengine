import unittest

import jovialengine.save as save


class TestSave(unittest.TestCase):
    def test_Save(self):
        # Act
        saves = save.Save.getAllFromFiles()
        # Assert
        self.assertEqual(len(saves), 1)
        save = saves[0]
        self.assertEqual(save.save_name, "a")
        self.assertEqual(save._mode_name, "ModeTest")
        self.assertEqual(save._mode_data, 1)
        self.assertEqual(save._shared_data, "test")


if __name__ == '__main__':
    unittest.main()
