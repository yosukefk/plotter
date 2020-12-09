import examples_bg as bg
import examples_bgm as bgm
import matplotlib as mpl
import unittest
import filecmp
from pathlib import Path

mpl.rcParams['savefig.dpi'] = 300

dir0 = Path('expected')
dir1 = Path('results')


class TestBackground(unittest.TestCase):
    def test_bg1(self):
        bg.tester_bg1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bg1.png',
            dir0 / 'test_bg1.png',
        ))

    def test_bg2(self):
        bg.tester_bg2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bg2.png',
            dir0 / 'test_bg2.png',
        ))
    def test_bg3(self):
        bg.tester_bg3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bg3.png',
            dir0 / 'test_bg3.png',
        ))
    def test_bg4(self):
        bg.tester_bg1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bg4.png',
            dir0 / 'test_bg4.png',
        ))

class TestBackgroundManager(unittest.TestCase):

    def test_bgm0(self):
        bgm.tester_bgm0()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm0.png',
            dir0 / 'test_bgm0.png',
        ))
    def test_bgm1(self):
        bgm.tester_bgm1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm1.png',
            dir0 / 'test_bgm1.png',
        ))
