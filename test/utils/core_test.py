import ew.utils.core as ewutils
import unittest

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

class NiceFormatTest(unittest.TestCase):

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

if __name__ == '__main__':
	unittest.main()