#!/usr/bin/env python3

import examples_solo as ex
import matplotlib as mpl
import unittest
import filecmp
from pathlib import Path
import warnings
from plotter.plotter_util import PlotterWarning



mpl.rcParams['savefig.dpi'] = 300

dir0 = Path('expected')
dir1 = Path('results')


class TestPlotter(unittest.TestCase):
    def test_r1(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_r1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_r1.png',
            dir1 / 'test_r1.png',
        ))

    def test_tr2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tr2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr2.png',
            dir1 / 'test_tr2.png',
        ))

    def test_tc2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tc2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc2.png',
            dir1 / 'test_tc2.png',
        ))

    def test_tr3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tr3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr3.png',
            dir1 / 'test_tr3.png',
        ))

    def test_tc3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tc3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc3.png',
            dir1 / 'test_tc3.png',
        ))

    def test_tr4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tr4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr4.png',
            dir1 / 'test_tr4.png',
        ))

    def test_tc4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_tc4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc4.png',
            dir1 / 'test_tc4.png',
        ))

    def test_pr2a(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pr2a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr2a.png',
            dir1 / 'test_pr2a.png',
        ))

    def test_pr2b(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pr2b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr2b.png',
            dir1 / 'test_pr2b.png',
        ))

    def test_pr2b_v(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pr2b_v(quiet=True)
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr2b.mp4',
            dir1 / 'test_pr2b.mp4',
        ))

    def test_pc2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pc2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc2.png',
            dir1 / 'test_pc2.png',
        ))

    def test_pc2_v(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pc2_v(quiet=True)
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc2.mp4',
            dir1 / 'test_pc2.mp4',
        ))

    def test_pr3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pr3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr3.png',
            dir1 / 'test_pr3.png',
        ))

    def test_pc3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pc3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc3.png',
            dir1 / 'test_pc3.png',
        ))

    def test_pr4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pr4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr4.png',
            dir1 / 'test_pr4.png',
        ))

    def test_pc4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_pc4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc4.png',
            dir1 / 'test_pc4.png',
        ))

    def test_s1a(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s1a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s1a.png',
            dir1 / 'test_s1a.png',
        ))

    def test_s1b(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s1b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s1b.png',
            dir1 / 'test_s1b.png',
        ))

    def test_s2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s2.png',
            dir1 / 'test_s2.png',
        ))

    def test_s3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s3.png',
            dir1 / 'test_s3.png',
        ))

    def test_s4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s4.png',
            dir1 / 'test_s4.png',
        ))

    def test_s5(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_s5(quiet=True)
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s5.png',
            dir1 / 'test_s5.png',
        ))
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s5.mp4',
            dir1 / 'test_s5.mp4',
        ))

if __name__ == '__main__':
    unittest.main()
