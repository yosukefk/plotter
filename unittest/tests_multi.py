#!/usr/bin/env python3

import examples_multi as ex
import matplotlib as mpl
import unittest
import filecmp
from pathlib import Path
import warnings
# TODO can i somehow supress warnings across board...?
from plotter.plotter_util import PlotterWarning



mpl.rcParams['savefig.dpi'] = 300

dir0 = Path('expected')
dir1 = Path('results')

class TestBackground(unittest.TestCase):

    def test_md1(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_md1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_md1.png',
            dir1 / 'test_md1.png',
        ))

    def test_md2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_md2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_md2.png',
            dir1 / 'test_md2.png',
        ))


    def test_md3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_md3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_md3.png',
            dir1 / 'test_md3.png',
        ))

    def test_md4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_md4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_md4.png',
            dir1 / 'test_md4.png',
        ))

    def test_mt1(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_mt1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_mt1.png',
            dir1 / 'test_mt1.png',
        ))

    def test_mt2(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_mt2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_mt2.png',
            dir1 / 'test_mt2.png',
        ))


    def test_mt3(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_mt3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_mt3.png',
            dir1 / 'test_mt3.png',
        ))

    def test_mt4(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=PlotterWarning)
            ex.tester_mt4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_mt4.png',
            dir1 / 'test_mt4.png',
        ))

if __name__ == '__main__':
    unittest.main()
