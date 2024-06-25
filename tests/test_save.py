import unittest
import os

import jovialengine.save as save

import mode


class TestSave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        save.init(
            os.path.join('.', 'saves'),
            mode
        )

    def test0_get_all_from_files(self):
        # Act
        saves = save.Save.get_all_from_files()
        # Assert
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].save_name, "a")
        self.assertEqual(saves[0]._mode_name, "ModeTest")
        self.assertEqual(saves[0]._mode_data, 1)
        self.assertEqual(saves[0]._shared_data, "test")

    def test1_will_overwrite(self):
        # Arrange
        colliding_name = "a"
        unique_name = "c"
        # Act
        colliding_result = save.Save.will_overwrite(colliding_name)
        unique_result = save.Save.will_overwrite(unique_name)
        # Assert
        self.assertEqual(colliding_result, True)
        self.assertEqual(unique_result, False)

    def test2_save_existing(self):
        # Arrange
        saves = save.Save.get_all_from_files()
        test_save = saves[0]
        test_save._mode_data = 2
        # Act
        test_save.save()
        saves = save.Save.get_all_from_files()
        # Assert
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0].save_name, "a")
        self.assertEqual(saves[0]._mode_name, "ModeTest")
        self.assertEqual(saves[0]._mode_data, 2)
        self.assertEqual(saves[0]._shared_data, "test")

    def test3_save_new(self):
        # Arrange
        saves = save.Save.get_all_from_files()
        test_save = saves[0]
        test_save.save_name = "b"
        test_save._mode_data = 2
        # Act
        test_save.save()
        saves = save.Save.get_all_from_files()
        # Assert
        self.assertEqual(len(saves), 2)
        self.assertEqual(saves[1].save_name, "b")
        self.assertEqual(saves[1]._mode_name, "ModeTest")
        self.assertEqual(saves[1]._mode_data, 2)
        self.assertEqual(saves[1]._shared_data, "test")

    def test4_save_delete(self):
        # Arrange
        saves = save.Save.get_all_from_files()
        # Act
        for test_save in saves:
            test_save.delete()
        saves = save.Save.get_all_from_files()
        # Assert
        self.assertEqual(len(saves), 0)


if __name__ == '__main__':
    unittest.main()
