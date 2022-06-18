import unittest

import jovialengine.save as save


class TestSave(unittest.TestCase):
    def test_getAllFromFiles(self):
        # Act
        saves = save.Save.getAllFromFiles()
        # Assert
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].save_name, "a")
        self.assertEqual(saves[0]._mode_name, "ModeTest")
        self.assertEqual(saves[0]._mode_data, 1)
        self.assertEqual(saves[0]._shared_data, "test")

    def test_save_existing(self):
        # Arrange
        saves = save.Save.getAllFromFiles()
        test_save = saves[0]
        test_save._mode_data = 2
        # Act
        test_save.save()
        saves = save.Save.getAllFromFiles()
        # Assert
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].save_name, "a")
        self.assertEqual(saves[0]._mode_name, "ModeTest")
        self.assertEqual(saves[0]._mode_data, 2)
        self.assertEqual(saves[0]._shared_data, "test")

    def test_save_new(self):
        # Arrange
        saves = save.Save.getAllFromFiles()
        test_save = saves[0]
        test_save.save_name = "b"
        test_save._mode_data = 2
        # Act
        test_save.save()
        saves = save.Save.getAllFromFiles()
        # Assert
        self.assertEqual(len(saves), 2)
        self.assertEqual(saves[1].save_name, "b")
        self.assertEqual(saves[1]._mode_name, "ModeTest")
        self.assertEqual(saves[1]._mode_data, 2)
        self.assertEqual(saves[1]._shared_data, "test")


if __name__ == '__main__':
    unittest.main()
