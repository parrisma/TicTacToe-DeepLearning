import unittest
from examples.gridworld.SimpleGridOne import SimpleGridOne
from examples.gridworld.IllegalGridMoveException import IllegalGridMoveException


class TestSimpleGridOne(unittest.TestCase):

    step = SimpleGridOne.STEP
    fire = SimpleGridOne.FIRE
    blck = SimpleGridOne.BLCK
    goal = SimpleGridOne.GOAL

    #
    # Test
    #
    def test_1(self):
        grid = [
            [self.step]
        ]
        sg1 = SimpleGridOne(1,
                            grid,
                            (0, 0),
                            (0, 0))
        alm = sg1.allowable_actions()
        self.assertEqual(alm, [])
        for actn in sg1.actions():
            self.assertRaises(IllegalGridMoveException, sg1.execute_action, actn)
        return

    #
    # Test
    #
    def test_2(self):
        grid = [
            [self.step, self.step],
            [self.step, self.step]
        ]
        sg1 = SimpleGridOne(1,
                            grid,
                            (0, 0),
                            (1, 1))
        alm = sg1.allowable_actions()
        self.assertEqual(alm, [])
        for actn in sg1.actions():
            self.assertRaises(IllegalGridMoveException, sg1.execute_action, actn)
        return

    def test_3(self):
        grid = [
            [self.step, self.fire, self.goal, self.step, self.step],
            [self.step, self.blck, self.blck, self.step, self.step],
            [self.step, self.blck, self.blck, self.blck, self.step],
            [self.step, self.step, self.step, self.step, self.step]
        ]
        return


#
# Execute the tests.
#


if __name__ == "__main__":
    if True:
        tests = TestSimpleGridOne()
        suite = unittest.TestLoader().loadTestsFromModule(tests)
        unittest.TextTestRunner().run(suite)
    else:
        suite = unittest.TestSuite()
        suite.addTest(TestSimpleGridOne("test_1"))
        unittest.TextTestRunner().run(suite)

