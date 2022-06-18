import unittest

import jovialengine.save as save

import constants


class TestSave(unittest.TestCase):
    def test_Save(self):
        print(constants.SAVE_DIRECTORY)
        saves = save.Save.getAllFromFiles()
        self.assertEqual(len(saves), 1)


if __name__ == '__main__':
    unittest.main()
