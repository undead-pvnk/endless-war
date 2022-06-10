import random
import unittest
from unittest.mock import MagicMock

import ew.utils.core as ewutils


class VectorTest(unittest.TestCase):

    def test_constructor(self):
        vector = ewutils.EwVector2D([1, 2])
        self.assertTrue(vector)
        self.assertEqual(vector.vector, [1, 2])

    def test_scalar_product(self):
        vector1 = ewutils.EwVector2D([1, 2])
        vector2 = ewutils.EwVector2D([3, 4])

        self.assertEqual(vector1.scalar_product(vector2), 11)

    def test_add(self):
        vector1 = ewutils.EwVector2D([1, 2])
        vector2 = ewutils.EwVector2D([3, 4])

        self.assertEqual(vector1.add(vector2).vector, [4, 6])

    def test_subtract(self):
        vector1 = ewutils.EwVector2D([1, 2])
        vector2 = ewutils.EwVector2D([3, 4])

        self.assertEqual(vector1.subtract(vector2).vector, [-2, -2])

    def test_norm(self):
        vector = ewutils.EwVector2D([3, 4])

        self.assertEqual(vector.norm(), 5)

    def test_normalize(self):
        vector = ewutils.EwVector2D([10, 0])

        self.assertEqual(vector.normalize().vector, [1, 0])


class UtilsTest(unittest.TestCase):

    def test_formatNiceList(self):
        self.assertEqual(ewutils.formatNiceList(['a', 'b', 'c']), 'a, b, and c')
        self.assertEqual(ewutils.formatNiceList(['a', 'b'], 'or'), 'a or b')

    def test_formatNiceTime(self):
        time_short = 23;
        time_medium = 2 * 60 + 4;
        time_long = 1 * 60 * 60 + 3 * 60 + 1

        self.assertEqual(ewutils.formatNiceTime(time_short), '23 seconds')
        self.assertEqual(ewutils.formatNiceTime(time_short, round_to_minutes=True), '0 minutes')
        self.assertEqual(ewutils.formatNiceTime(time_short, round_to_hours=True), '0 hours')

        self.assertEqual(ewutils.formatNiceTime(time_medium), '2 minutes and 4 seconds')
        self.assertEqual(ewutils.formatNiceTime(time_medium, round_to_minutes=True), '2 minutes')
        self.assertEqual(ewutils.formatNiceTime(time_medium, round_to_hours=True), '0 hours')

        self.assertEqual(ewutils.formatNiceTime(time_long), '1 hour, 3 minutes, and 1 second')
        self.assertEqual(ewutils.formatNiceTime(time_long, round_to_minutes=True), '1 hour and 3 minutes')
        self.assertEqual(ewutils.formatNiceTime(time_long, round_to_hours=True), '1 hour')

    def test_weightedChoice(self):
        random.random = MagicMock(return_value=0.1)

        weight_map = {
            'a': 1,
            'b': 8
        }

        self.assertEqual(ewutils.weightedChoice(weight_map), 'a')

    def test_userListToNameString(self):
        class UserMock:
            display_name = ''

            def __init__(self, name):
                self.display_name = name

        user_a = UserMock('a')
        user_b = UserMock('b')
        user_c = UserMock('c')

        self.assertEqual(ewutils.userListToNameString([user_a]), 'a')
        self.assertEqual(ewutils.userListToNameString([user_a, user_b]), 'a and b')
        self.assertEqual(ewutils.userListToNameString([user_a, user_b, user_c]), 'a, b, and c')

    def test_getRoleMap(self):
        class RoleMock:
            name = ''

            def __init__(self, name):
                self.name = name

        role_a = RoleMock('Role A')
        role_b = RoleMock('Role B')

        self.assertEqual(ewutils.getRoleMap([role_a, role_b]), {'rolea': role_a, 'roleb': role_b})

    def test_getRoleIdMap(self):
        class RoleMock:
            id = ''

            def __init__(self, id):
                self.id = id

        role_a = RoleMock(1)
        role_b = RoleMock(2)

        self.assertEqual(ewutils.getRoleIdMap([role_a, role_b]), {1: role_a, 2: role_b})

    def test_mapRoleName(self):
        self.assertEqual(ewutils.mapRoleName(123), 123)
        self.assertEqual(ewutils.mapRoleName('test'), 'test')
        self.assertEqual(ewutils.mapRoleName('More Complicated Test'), 'morecomplicatedtest')

    def test_getIntToken(self):
        self.assertEqual(ewutils.getIntToken([]), None)
        self.assertEqual(ewutils.getIntToken(['test']), None)
        self.assertEqual(ewutils.getIntToken(['1']), None)
        self.assertEqual(ewutils.getIntToken(['1', '2']), 2)
        self.assertEqual(ewutils.getIntToken(['2', '1,200']), 1200)
        self.assertEqual(ewutils.getIntToken(['1', 'test', '2']), 2)
        self.assertEqual(ewutils.getIntToken(['test', '-1']), None)
        self.assertEqual(ewutils.getIntToken(['test', 'all', '-1'], negate=True), 1)
        self.assertEqual(ewutils.getIntToken(['test', 'all', '2'], allow_all=True), -1)
        self.assertEqual(ewutils.getIntToken(['test', '2', 'all'], allow_all=True), 2)

    def test_flattenTokenListToString(self):
        self.assertEqual(ewutils.flattenTokenListToString(['Test', ':Success']), 'testsuccess')
        self.assertEqual(ewutils.flattenTokenListToString(" '\"!@#$%^&*().,/?{}[];:"), "")
        self.assertEqual(ewutils.flattenTokenListToString(['Test', '<@1234>', 'Success']), 'testsuccess')


if __name__ == '__main__':
    unittest.main()
