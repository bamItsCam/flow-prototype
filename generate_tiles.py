#!/usr/local/bin/python3

# A = corner
# B = line
# C = nub
# D = blank
import copy
from dataclasses import dataclass
from typing import Tuple, List
from itertools import product
from PIL import Image, ImageDraw
from enum import Enum

top_index = 0
right_index = 1
bot_index = 2
left_index = 3

PX_PER_TILE = 200
LINE_WIDTH_PCT = 0.06

top_pt = (0.5, 0)
right_pt = (1, 0.5)
bot_pt = (0.5, 1)
left_pt = (0, 0.5)


class ShapeType(Enum):
    CORNER = "corner"
    LINE = "line"
    NUB = "nub"
    BLANK = "blank"
    TEE = "tee"


class Color(Enum):
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    LIGHT_GREY = (224, 224, 224, 255)
    RED = (255, 51, 51, 255)
    ORANGE = (255, 153, 51, 255)
    YELLOW = (255, 255, 51, 255)
    GREEN = (51, 255, 51, 255)
    BLUE = (0, 0, 255, 255)
    PURPLE = (153, 51, 255, 255)
    PINK = (255, 51, 255, 255)


class SideNode:
    def __init__(self, shape_type: ShapeType, point: Tuple[float, float]):
        self.shape_type = shape_type
        self.point = point
        self.reserved = False

    def reserve(self):
        self.reserved = True


def index_rollover(original_position: int, size: int, increase: int) -> int:
    return (original_position + increase) % size


# Shape captures the necessary methods to draw a shape within a square canvas
class Shape:
    def __init__(self, shape_type: ShapeType, points, canvas_px: int):
        self.shape_type = shape_type
        self.color = Color.WHITE
        self.canvas_px = canvas_px
        self.points = points

    def __str__(self):
        return f'{self.shape_type.value} {self.points} {self.color}'

    def draw(self, draw: ImageDraw):
        pass

    def set_color(self, color: Color):
        self.color = color

    def __eq__(self, other):
        if not isinstance(other, Shape):
            # don't attempt to compare against unrelated types
            return NotImplemented

        # When deduping rotationally symmetrical shape/color pairs, ignoring position is necessary
        return self.shape_type.value == other.shape_type.value and \
               self.color.value == other.color.value

@dataclass(eq=False)
class Corner(Shape):
    def __init__(self, points: List[Tuple[float, float]], canvas_px: int):
        Shape.__init__(self, ShapeType.CORNER, points, canvas_px)
        if len(points) != 2:
            raise Exception
        else:
            self.pta = points[0]
            self.ptb = points[1]

    def draw(self, draw: ImageDraw):
        # top right
        if self.pta == top_pt and self.ptb == right_pt or self.pta == right_pt and self.ptb == top_pt:
            circle_xy0 = (0.5, -0.5)
            circle_xy1 = (1.5, 0.5)
            start_deg = 90
            end_deg = 180
        # bot right
        elif self.pta == bot_pt and self.ptb == right_pt or self.pta == right_pt and self.ptb == bot_pt:
            circle_xy0 = (0.5, 0.5)
            circle_xy1 = (1.5, 1.5)
            start_deg = 180
            end_deg = 270
        # bot left
        elif self.pta == bot_pt and self.ptb == left_pt or self.pta == left_pt and self.ptb == bot_pt:
            circle_xy0 = (-0.5, 0.5)
            circle_xy1 = (0.5, 1.5)
            start_deg = 270
            end_deg = 360
        # top left
        elif self.pta == top_pt and self.ptb == left_pt or self.pta == left_pt and self.ptb == top_pt:
            circle_xy0 = (-0.5, -0.5)
            circle_xy1 = (0.5, 0.5)
            start_deg = 0
            end_deg = 90
        else:
            raise Exception

        circle_xy0_px = tuple_multiply(circle_xy0, self.canvas_px)
        circle_xy1_px = tuple_multiply(circle_xy1, self.canvas_px)

        #print(f'{(circle_xy0_px, circle_xy1_px)}, {start_deg}, {end_deg},{int(self.canvas_px * LINE_WIDTH_PCT)}')

        draw.arc((circle_xy0_px, circle_xy1_px), start_deg, end_deg, fill=self.color.value,
                 width=int(self.canvas_px * LINE_WIDTH_PCT))

        return

@dataclass(eq=False)
class Line(Shape):
    def __init__(self, points: List[Tuple[float, float]], canvas_px: int):
        Shape.__init__(self, ShapeType.LINE, points, canvas_px)
        if len(points) != 2:
            raise Exception
        else:
            self.pta = points[0]
            self.ptb = points[1]

    def draw(self, draw: ImageDraw):
        # top bot
        if self.pta == top_pt and self.ptb == bot_pt or self.pta == bot_pt and self.ptb == top_pt:
            xy0 = top_pt
            xy1 = bot_pt
        # left right
        elif self.pta == left_pt and self.ptb == right_pt or self.pta == right_pt and self.ptb == left_pt:
            xy0 = left_pt
            xy1 = right_pt
        else:
            raise Exception

        xy0_px = tuple_multiply(xy0, self.canvas_px)
        xy1_px = tuple_multiply(xy1, self.canvas_px)

        draw.line((xy0_px, xy1_px), self.color.value, width=int(self.canvas_px * LINE_WIDTH_PCT))

        return

@dataclass(eq=False)
class Tee(Shape):
    def __init__(self, points: List[Tuple[float, float, float]], canvas_px: int):
        Shape.__init__(self, ShapeType.TEE, points, canvas_px)
        if len(points) != 3:
            raise Exception

    def draw(self, draw: ImageDraw):
        xy1 = (0.5, 0.5) # middle
        for pt in self.points:
            # top
            if pt == top_pt:
                xy0 = top_pt
            # right
            elif pt == right_pt:
                xy0 = right_pt
            # bot
            elif pt == bot_pt:
                xy0 = bot_pt
            # left
            elif pt == left_pt:
                xy0 = left_pt
            else:
                raise Exception(f'pt is {pt.__str__}, type {type(pt)}')

            xy0_px = tuple_multiply(xy0, self.canvas_px)
            xy1_px = tuple_multiply(xy1, self.canvas_px)

            draw.line((xy0_px, xy1_px), self.color.value, width=int(self.canvas_px * LINE_WIDTH_PCT), joint="curve")

        return

@dataclass(eq=False)
class Nub(Shape):
    def __init__(self, points: Tuple[float, float], canvas_px: int):
        Shape.__init__(self, ShapeType.NUB, points, canvas_px)
        self.pt = points

    def draw(self, draw: ImageDraw):
        nub_length = 0.25
        # top
        if self.pt == top_pt:
            xy0 = top_pt
            xy1 = (top_pt[0], top_pt[1] + nub_length)
        # right
        elif self.pt == right_pt:
            xy0 = right_pt
            xy1 = (right_pt[0] - nub_length, right_pt[1])
        # bot
        elif self.pt == bot_pt:
            xy0 = bot_pt
            xy1 = (bot_pt[0], bot_pt[1] - nub_length)
        # left
        elif self.pt == left_pt:
            xy0 = left_pt
            xy1 = (left_pt[0] + nub_length, left_pt[1])
        else:
            raise Exception

        xy0_px = tuple_multiply(xy0, self.canvas_px)
        xy1_px = tuple_multiply(xy1, self.canvas_px)

        draw.line((xy0_px, xy1_px), self.color.value, width=int(self.canvas_px * LINE_WIDTH_PCT), joint="curve")

        return

@dataclass(eq=False)
class Blank(Shape):
    def __init__(self):
        Shape.__init__(self, ShapeType.BLANK, None, PX_PER_TILE)

    def draw(self, draw: ImageDraw):
        pass

    def set_color(self, color: Color):
        pass


class ColoredTile:
    def __init__(self, shapes: List[Shape]):
        self.shapes = shapes

    def __str__(self):
        return f'Shapes: {[str(s) for s in self.shapes ]}'
        #return f'{self.shapes}'

    def draw(self, draw: ImageDraw):
        for shape in self.shapes:
            shape.draw(draw)

    def __eq__(self, other):
        if not isinstance(other, ColoredTile):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return sorted(self.shapes, key=lambda s: (s.shape_type.value, s.color.value)) == sorted(other.shapes, key=lambda s: (s.shape_type.value, s.color.value))


class TilePattern:
    def __init__(self, sides: Tuple[ShapeType, ShapeType, ShapeType, ShapeType]):
        self.shapes = []
        side_nodes = (
            SideNode(sides[top_index], top_pt),
            SideNode(sides[right_index], right_pt),
            SideNode(sides[bot_index], bot_pt),
            SideNode(sides[left_index], left_pt)
        )
        for i in range(4):
            # keep "rotating" the tile, comparing sides to find legal shapes,
            # then mark the sides with a found shape as "reserved"
            this_side = side_nodes[i]
            right_side = side_nodes[index_rollover(right_index, 4, i)]
            opposite_side = side_nodes[index_rollover(bot_index, 4, i)]
            #left_side = SideNodes[index_rollover(left_index, 4, i)]

            if this_side.reserved:
                continue

            if this_side.shape_type == ShapeType.BLANK:
                this_side.reserve()
                blank = Blank()
                self.shapes.append(blank)

            elif this_side.shape_type == ShapeType.NUB:
                this_side.reserve()
                nub = Nub(this_side.point, PX_PER_TILE)
                self.shapes.append(nub)

            elif this_side.shape_type == ShapeType.LINE:
                if not opposite_side.reserved and opposite_side.shape_type == ShapeType.LINE:
                    # we've found a line between this and the opposite side
                    this_side.reserve()
                    opposite_side.reserve()
                    line = Line([this_side.point, opposite_side.point], PX_PER_TILE)
                    self.shapes.append(line)

            elif this_side.shape_type == ShapeType.CORNER:
                if not right_side.reserved and right_side.shape_type == ShapeType.CORNER:
                    # we've found a corner between two side nodes
                    this_side.reserve()
                    right_side.reserve()
                    corner = Corner([this_side.point, right_side.point], PX_PER_TILE)
                    self.shapes.append(corner)

            elif this_side.shape_type == ShapeType.TEE:
                if not right_side.reserved and right_side.shape_type == ShapeType.TEE and \
                        not opposite_side.reserved and opposite_side.shape_type == ShapeType.TEE:
                    # we've found a tee between three side nodes
                    this_side.reserve()
                    right_side.reserve()
                    opposite_side.reserve()
                    tee = Tee([this_side.point, right_side.point, opposite_side.point], PX_PER_TILE)
                    self.shapes.append(tee)

            else:
                raise Exception("unknown shape type")

    def generate_colored(self, colors: List[Color]) -> List[ColoredTile]:
        colored_tiles = []
        colored_shapes = []
        for s in self.shapes:
            colored_shapes.append(list(product([s], colors, repeat=1)))

        tiles_shapes_colors_tuples = list(product(*colored_shapes))

        for tile_shapes_colors_tuples in tiles_shapes_colors_tuples:
            colored_shapes = []
            for shape_color_tuple in tile_shapes_colors_tuples:
                shape = copy.copy(shape_color_tuple[0])
                color = shape_color_tuple[1]
                shape.set_color(color)
                colored_shapes.append(shape)

            new_tile = ColoredTile(colored_shapes)
            if new_tile not in colored_tiles:
                colored_tiles.append(new_tile)
        return colored_tiles


def tuple_multiply(t: Tuple, multiple: int) -> Tuple:
    return tuple(multiple * x for x in t)


def tuple_add(t: Tuple, addition: int) -> Tuple:
    return tuple(x + addition for x in t)


def get_all_products() -> list:
    return list(product([ShapeType.CORNER, ShapeType.LINE, ShapeType.BLANK, ShapeType.TEE], repeat=4))


def filter_illegal(unfiltered: list) -> list:
    def apply_filter_blank(unfiltered: list) -> list:
        # technically, blanks can go anywhere since the only depend on a single Side node; however
        # we don't really want a tile of 4 blank sides, for example
        # so, drop all tiles with 3 or 4 blank sides
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-1-2-3-4-5-6-8-9-10-12___________option-0_____899788975471827592721
        filtered = []
        for p in unfiltered:
            # A'B' + A'C' + B'C' + A'D' + B'D' + C'D'
            top = p[top_index] == ShapeType.BLANK
            right = p[right_index] == ShapeType.BLANK
            bot = p[bot_index] == ShapeType.BLANK
            left = p[left_index] == ShapeType.BLANK
            if (
                    (not top and not right)
                    or (not top and not bot)
                    or (not right and not bot)
                    or (not top and not left)
                    or (not right and not left)
                    or (not bot and not left)
            ):
                filtered.append(p)

        return filtered

    def apply_filter_corner(unfiltered: list) -> list:
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-3-6-9-12-15___________option-0_____989780977179845392647
        filtered = []
        for p in unfiltered:
            top = p[top_index] == ShapeType.CORNER
            right = p[right_index] == ShapeType.CORNER
            bot = p[bot_index] == ShapeType.CORNER
            left = p[left_index] == ShapeType.CORNER
            if (
                    (not top and not right and not bot and not left)
                    or (not top and not right and bot and left)
                    or (not top and right and bot and not left)
                    or (top and not right and not bot and left)
                    or (top and right and not bot and not left)
                    or (top and right and bot and left)
            ):
                filtered.append(p)

        return filtered

    def apply_filter_line(unfiltered: list) -> list:
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-5-10-15___________option-0_____999782971575855597795
        filtered = []
        for p in unfiltered:
            top = p[top_index] == ShapeType.LINE
            right = p[right_index] == ShapeType.LINE
            bot = p[bot_index] == ShapeType.LINE
            left = p[left_index] == ShapeType.LINE
            if (
                    (not top and not right and not bot and not left)
                    or (not top and right and not bot and left)
                    or (top and not right and bot and not left)
                    or (top and right and bot and left)
            ):
                filtered.append(p)

        return filtered

    def apply_filter_tee(unfiltered: list) -> list:
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-7-11-13-14___________option-0_____989784860978820592709
        filtered = []
        for p in unfiltered:
            top = p[top_index] == ShapeType.TEE
            right = p[right_index] == ShapeType.TEE
            bot = p[bot_index] == ShapeType.TEE
            left = p[left_index] == ShapeType.TEE
            if (
                    (not top and not right and not bot and not left)
                    or (not top and right and bot and left)
                    or (top and not right and bot and left)
                    or (top and right and not bot and left)
                    or (top and right and bot and not left)
            ):
                filtered.append(p)

        return filtered

    return apply_filter_blank(apply_filter_tee(apply_filter_line(apply_filter_corner(unfiltered))))


def dedupe_rotational_symmetry(duped: list) -> list:
    deduped = []
    for d in duped:
        is_dupe = False
        for i in range(4):
            shifted = (
                d[index_rollover(0, 4, i)],
                d[index_rollover(1, 4, i)],
                d[index_rollover(2, 4, i)],
                d[index_rollover(3, 4, i)]
            )
            if shifted in deduped:
                is_dupe = True
                break
        if not is_dupe:
            deduped.append(d)

    return deduped


def main():
    legal_shape_layouts = dedupe_rotational_symmetry(filter_illegal(get_all_products()))
    print(len(legal_shape_layouts))

    legal_shape_layouts = [(ShapeType.CORNER, ShapeType.CORNER, ShapeType.CORNER, ShapeType.CORNER)]
    colored_tiles = []
    colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUE, Color.PURPLE, Color.PINK]
    for shapes in legal_shape_layouts:
        pattern = TilePattern(shapes)
        new_tiles = pattern.generate_colored(colors)
        for tile in new_tiles:
            print(str(tile))
        colored_tiles = colored_tiles + new_tiles

        for tile in new_tiles:
            im = Image.new('RGBA', (PX_PER_TILE, PX_PER_TILE), Color.LIGHT_GREY.value)
            drawer = ImageDraw.Draw(im)
            tile.draw(drawer)

            im.show()
    print(len(colored_tiles))


if __name__ == "__main__":
    main()
