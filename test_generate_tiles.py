from unittest import TestCase

from generate_tiles import *

class Test(TestCase):
    def test_dedupe(self):
        dupe_list = [
            (ShapeType.NUB, ShapeType.NUB, ShapeType.BLANK, ShapeType.BLANK),
            (ShapeType.NUB, ShapeType.BLANK, ShapeType.BLANK, ShapeType.NUB)
        ]
        unduped = dedupe_rotational_symmetry(dupe_list)
        self.assertEqual([(ShapeType.NUB, ShapeType.NUB, ShapeType.BLANK, ShapeType.BLANK)], unduped)


class TestShape(TestCase):
    def test_eq_corner(self):
        corner1 = Corner([(0, 0), (1, 1)], PX_PER_TILE)
        corner2 = Corner([(0, 0), (1, 1)], PX_PER_TILE)
        corner3 = Corner([(0, 1), (1, 1)], PX_PER_TILE)
        self.assertEqual(corner1, corner2)
        # Check that equals ignores position
        self.assertEqual(corner1, corner3)


class TestColoredTile(TestCase):
    def test_eq(self):
        green_corner1 = Corner([(0, 0), (1, 1)], PX_PER_TILE)
        green_corner1.set_color(Color.GREEN)
        green_corner2 = Corner([(1, 0), (1, 1)], PX_PER_TILE)
        green_corner2.set_color(Color.GREEN)
        green_nub1 = Nub((0, 1), PX_PER_TILE)
        green_nub1.set_color(Color.GREEN)
        green_nub2 = Nub((1, 1), PX_PER_TILE)
        green_nub2.set_color(Color.GREEN)
        red_corner1 = Corner([(0, 0), (1, 0)], PX_PER_TILE)
        red_corner1.set_color(Color.RED)
        red_corner2 = Corner([(1, 0), (1, 0)], PX_PER_TILE)
        red_corner2.set_color(Color.RED)
        red_nub1 = Nub((0, 1), PX_PER_TILE)
        red_nub1.set_color(Color.RED)
        red_nub2 = Nub((1, 1), PX_PER_TILE)
        red_nub2.set_color(Color.RED)
        tile1 = ColoredTile([green_corner1, green_corner2, green_nub1, green_nub2])
        tile2 = ColoredTile([green_corner1, green_corner2, red_nub1, green_nub2])
        self.assertNotEqual(tile1, tile2)

        tile3 = ColoredTile([green_nub1, green_nub2, red_nub1, red_nub2])
        tile4 = ColoredTile([red_nub1, red_nub2, green_nub1, green_nub2])
        tile5 = ColoredTile([red_nub1, green_nub1, green_nub1, green_nub2])
        self.assertEqual(tile3, tile4)
        self.assertNotEqual(tile3, tile5)


class TestTilePattern(TestCase):
    def test_generate_colored(self):
        blank = Blank()
        red_right_nub = Nub((right_pt), PX_PER_TILE)
        green_right_nub = Nub((right_pt), PX_PER_TILE)
        tile1 = TilePattern((ShapeType.BLANK, ShapeType.BLANK, ShapeType.BLANK, ShapeType.NUB))
        red_right_nub.set_color(Color.RED)
        green_right_nub.set_color(Color.GREEN)
        generated = tile1.generate_colored([Color.RED, Color.GREEN])
        expected = [ColoredTile([blank, blank, blank, green_right_nub]), ColoredTile([blank, blank, blank, red_right_nub])]
        self.assertCountEqual(generated, expected)
