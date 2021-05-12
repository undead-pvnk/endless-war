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



if __name__ == '__main__':
	unittest.main()