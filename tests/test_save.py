import unittest
import sys
import os
sys.path.append(
    os.path.dirname(os.path.realpath(__file__)) + "/../src/jovialengine"
)
import save


class TestSave(unittest.TestCase):
    def test_Save(self):
        saves = save.Save.getAllFromFiles()
        self.assertEqual(len(saves), 0)

if __name__ == '__main__':
    unittest.main()
