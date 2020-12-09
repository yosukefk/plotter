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

    def test_bgm_n0(self):
        bgm.tester_bgm_n0()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_n0.png',
            dir0 / 'test_bgm_n0.png',
        ))

    def test_bgm_n1(self):
        bgm.tester_bgm_n1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_n1.png',
            dir0 / 'test_bgm_n1.png',
        ))

    def test_bgm_n2(self):
        bgm.tester_bgm_n2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_n2.png',
            dir0 / 'test_bgm_n2.png',
        ))

    def test_bgm_n3(self):
        bgm.tester_bgm_n3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_n3.png',
            dir0 / 'test_bgm_n3.png',
        ))

    def test_bgm_n4(self):
        bgm.tester_bgm_n4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_n4.png',
            dir0 / 'test_bgm_n4.png',
        ))

    def test_bgm_b1a(self):
        bgm.tester_bgm_b1a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b1a.png',
            dir0 / 'test_bgm_b1a.png',
        ))

    def test_bgm_b1b(self):
        bgm.tester_bgm_b1b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b1b.png',
            dir0 / 'test_bgm_b1b.png',
        ))

    def test_bgm_b1c(self):
        bgm.tester_bgm_b1c()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b1c.png',
            dir0 / 'test_bgm_b1c.png',
        ))

    def test_bgm_b2a(self):
        bgm.tester_bgm_b2a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b2a.png',
            dir0 / 'test_bgm_b2a.png',
        ))

    def test_bgm_b2b(self):
        bgm.tester_bgm_b2b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b2b.png',
            dir0 / 'test_bgm_b2b.png',
        ))

    def test_bgm_b3(self):
        bgm.tester_bgm_b3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b3.png',
            dir0 / 'test_bgm_b3.png',
        ))

    def test_bgm_b4a(self):
        bgm.tester_bgm_b4a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b4a.png',
            dir0 / 'test_bgm_b4a.png',
        ))

    def test_bgm_b4b(self):
        bgm.tester_bgm_b4b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_b4b.png',
            dir0 / 'test_bgm_b4b.png',
        ))

    def test_bgm_w1(self):
        bgm.tester_bgm_w1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w1.png',
            dir0 / 'test_bgm_w1.png',
        ))

    def test_bgm_w2a(self):
        bgm.tester_bgm_w2a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w2a.png',
            dir0 / 'test_bgm_w2a.png',
        ))

    def test_bgm_w2b(self):
        bgm.tester_bgm_w2b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w2b.png',
            dir0 / 'test_bgm_w2b.png',
        ))
    def test_bgm_w2c(self):
        bgm.tester_bgm_w2c()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w2c.png',
            dir0 / 'test_bgm_w2c.png',
        ))
    def test_bgm_w3(self):
        bgm.tester_bgm_w3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w3.png',
            dir0 / 'test_bgm_w3.png',
        ))
    def test_bgm_w4(self):
        bgm.tester_bgm_w4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_bgm_w4.png',
            dir0 / 'test_bgm_w4.png',
        ))
