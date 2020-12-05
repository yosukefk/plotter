import examples as ex
import unittest
import filecmp
from pathlib import Path

dir0 = Path('expected')
dir1 = Path('results')


class MyTestCase(unittest.TestCase):
    def test_r1(self):
        ex.tester_r1()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_r1.png',
            dir0 / 'test_r1.png',
        ))

    def test_tr2(self):
        ex.tester_tr2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr2.png',
            dir0 / 'test_tr2.png',
        ))

    def test_tc2(self):
        ex.tester_tc2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc2.png',
            dir0 / 'test_tc2.png',
        ))

    def test_tr3(self):
        ex.tester_tr3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr3.png',
            dir0 / 'test_tr3.png',
        ))

    def test_tc3(self):
        ex.tester_tc3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc3.png',
            dir0 / 'test_tc3.png',
        ))

    def test_tr4(self):
        ex.tester_tr4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tr4.png',
            dir0 / 'test_tr4.png',
        ))

    def test_tc4(self):
        ex.tester_tc4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_tc4.png',
            dir0 / 'test_tc4.png',
        ))

    def test_pr2a(self):
        ex.tester_pr2a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr2a.png',
            dir0 / 'test_pr2a.png',
        ))

    def test_pr2b(self):
        ex.tester_pr2b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr2b.png',
            dir0 / 'test_pr2b.png',
        ))

    def test_pc2(self):
        ex.tester_pc2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc2.png',
            dir0 / 'test_pc2.png',
        ))

    def test_pr3(self):
        ex.tester_pr3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr3.png',
            dir0 / 'test_pr3.png',
        ))

    def test_pc3(self):
        ex.tester_pc3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc3.png',
            dir0 / 'test_pc3.png',
        ))

    def test_pr4(self):
        ex.tester_pr4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pr4.png',
            dir0 / 'test_pr4.png',
        ))

    def test_pc4(self):
        ex.tester_pc4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_pc4.png',
            dir0 / 'test_pc4.png',
        ))

    def test_s1a(self):
        ex.tester_s1a()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s1a.png',
            dir0 / 'test_s1a.png',
        ))

    def test_s1b(self):
        ex.tester_s1b()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s1b.png',
            dir0 / 'test_s1b.png',
        ))

    def test_s2(self):
        ex.tester_s2()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s2.png',
            dir0 / 'test_s2.png',
        ))

    def test_s3(self):
        ex.tester_s3()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s3.png',
            dir0 / 'test_s3.png',
        ))

    def test_s4(self):
        ex.tester_s4()
        self.assertTrue(filecmp.cmp(
            dir0 / 'test_s4.png',
            dir0 / 'test_s4.png',
        ))


if __name__ == '__main__':
    unittest.main()
