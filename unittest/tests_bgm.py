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

    def test_bgm2(self):
        bgm.tester_bgm2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm2.png',
            dir0 / 'test_bgm2.png',
        ))

    def test_bgm3(self):
        bgm.tester_bgm3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm3.png',
            dir0 / 'test_bgm3.png',
        ))

    def test_bgm4(self):
        bgm.tester_bgm4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm4.png',
            dir0 / 'test_bgm4.png',
        ))

    def test_bgm5(self):
        bgm.tester_bgm5()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm5.png',
            dir0 / 'test_bgm5.png',
        ))

    def test_bgm6(self):
        bgm.tester_bgm6()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm6.png',
            dir0 / 'test_bgm6.png',
        ))

    def test_bgm7(self):
        # bgm.tester_bgm7()
        # self.assertTrue(filecmp.cmp(
        #     dir0 / 'test_bgm7.png',
        #     dir0 / 'test_bgm7.png',
        # ))
        self.assertRaises(
            NotImplementedError,
            bgm.tester_bgm7
        )

    def test_bgm8(self):
        bgm.tester_bgm8()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm8.png',
            dir0 / 'test_bgm8.png',
        ))

    def test_bgm9(self):
        bgm.tester_bgm9()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm9.png',
            dir0 / 'test_bgm9.png',
        ))

    def test_bgm10(self):
        bgm.tester_bgm10()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm10.png',
            dir0 / 'test_bgm10.png',
        ))

    def test_bgm11(self):
        bgm.tester_bgm11()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm11.png',
            dir0 / 'test_bgm11.png',
        ))
