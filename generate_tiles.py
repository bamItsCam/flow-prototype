#!/usr/local/bin/python3

# A = corner
# B = line
# C = nub
# D = blank

from typing import Tuple, List
from itertools import product
from PIL import Image, ImageDraw
from enum import Enum

top_index=0
right_index=1
bot_index=2
left_index=3

PX_PER_TILE=200
LINE_WIDTH_PCT=0.06

top_pt=(0.5, 0)
right_pt=(1, 0.5)
bot_pt=(0.5, 1)
left_pt=(0, 0.5)

class ShapeType(Enum):
    CORNER = "corner"
    LINE = "line"
    NUB = "nub"
    BLANK = "blank"

class Color(Enum):
    WHITE = (255,255,255,255)
    BLACK = (0,0,0,255)
    LIGHT_GREY = (216, 216, 216, 255)

class SideNode:
    def __init__(self, shape_type: ShapeType, point: Tuple[float, float]):
        self.shape_type = shape_type
        self.point = point
    def reserve(self):
        self.reserved = True

class Tile:
    def __init__(self, sides: Tuple[ShapeType, ShapeType, ShapeType, ShapeType]):
        self.shapes = []
        SideNodes = (
            SideNode(sides[top_index], top_pt), 
            SideNode(sides[right_index], right_pt), 
            SideNode(sides[bot_index], bot_pt), 
            SideNode(sides[left_index], left_pt)
        )
        for i in range(4):
            # keep "rotating" the tile, comparing sides to find matching shapes,
            # then mark the sides with a found shape as "reserved"
            thisSide=SideNodes[i]
            rightSide=SideNodes[index_rollover(right_index, 4, i)]
            oppositeSide=SideNodes[index_rollover(bot_index, 4, i)]
            leftSide=SideNodes[index_rollover(left_index, 4, i)]

            if thisSide.shape_type == ShapeType.BLANK:
                thisSide.reserve()
                blank = Blank()
                self.shapes.append(blank)
                
            elif thisSide.shape_type == ShapeType.NUB:
                thisSide.reserve()
                nub = Nub(thisSide.point, Color.BLACK, PX_PER_TILE)
                self.shapes.append(nub)
            
            elif thisSide.shape_type == ShapeType.LINE:
                if oppositeSide.shape_type == ShapeType.LINE:
                    # we've found a line between this and the opposite side
                    thisSide.reserve()
                    oppositeSide.reserve()
                    line = Line([thisSide.point, oppositeSide.point], Color.BLACK, PX_PER_TILE)
                    self.shapes.append(line)

            elif thisSide.shape_type == ShapeType.CORNER:
                if rightSide.shape_type == ShapeType.CORNER:
                    # we've found a corner between two side nodes
                    thisSide.reserve()
                    rightSide.reserve()
                    corner = Corner([thisSide.point, rightSide.point], Color.BLACK, PX_PER_TILE)
                    self.shapes.append(corner)
            
            else:
                raise Exception("unknown shape type")

        print(SideNodes)


def index_rollover(original_position: int, size: int, increase: int) -> int:
    return (original_position + increase) % size


# Shape captures the necessary methods to draw a shape within a square canvas
class Shape:
    def __init__(self, points: List[Tuple[float, float]], shape_type: ShapeType, color: Tuple[int, int, int, int], canvas_px: int):
        self.shape_type = shape_type
        self.color = color
        self.canvas_px = canvas_px
        self.points = points

    def draw(self, draw: ImageDraw):
       pass

class Corner(Shape):
    def __init__(self, points: List[Tuple[float, float]], color: Tuple[int, int, int, int], canvas_px: int):
        Shape.__init__(self, points, ShapeType.CORNER, color, canvas_px)
        if len(points) != 2:
            raise Exception
        else:
            self.pta = points[0]
            self.ptb = points[1]

    def draw(self, draw: ImageDraw):
        # top right
        if self.pta == (0.5,0) and self.ptb == (1,0.5) or self.pta == (1,0.5) and self.ptb == (0.5,0):
            circle_xy0=(1.5,-0.5)
            start_deg=90
            end_deg=180
        # bot right
        elif self.pta == (0.5,1) and self.ptb == (1,0.5) or self.pta == (1,0.5) and self.ptb == (0.5,1):
            circle_xy0=(1.5,1.5)
            start_deg=180
            end_deg=270
        # bot left
        elif self.pta == (0,0.5) and self.ptb == (0.5,1) or self.pta == (0.5,1) and self.ptb == (0,0.5):
            circle_xy0=(-0.5,1.5)
            start_deg=180
            end_deg=270
        # top left
        elif self.pta == (0.5,0) and self.ptb == (0,0.5) or self.pta == (0,0.5) and self.ptb == (0.5,0):
            circle_xy0=(-0.5,-0.5)
            start_deg=0
            end_deg=90
        else:
            raise Exception

        circle_xy0_px=tuple_multiply(circle_xy0, self.canvas_px)
        circle_xy1_px=tuple_multiply((0.5, 0.5), self.canvas_px)

        print(f'{(circle_xy0_px,circle_xy1_px)}, {start_deg}, {end_deg},{int(self.canvas_px*LINE_WIDTH_PCT)}')
        
        draw.arc((circle_xy0_px,circle_xy1_px), start_deg, end_deg, fill=self.color.value, width=int(self.canvas_px*LINE_WIDTH_PCT))

        return

class Line(Shape):
    def __init__(self, points: List[Tuple[float, float]], color: Tuple[int, int, int, int], canvas_px: int):
        Shape.__init__(self, points, ShapeType.LINE, color, canvas_px)
        if len(points) != 2:
            raise Exception
        else:
            self.pta = points[0]
            self.ptb = points[1]

    def draw(self, draw: ImageDraw):
        pass


class Nub(Shape):
    def __init__(self, points: Tuple[float, float], color: Tuple[int, int, int, int], canvas_px: int):
        Shape.__init__(self, points, ShapeType.NUB, color, canvas_px)
        self.pt = points

class Blank(Shape):
    def __init__(self):
        pass

    def draw(self, draw: ImageDraw):
        pass

def tuple_multiply(t: Tuple, multiple: int) -> Tuple:
    return tuple(multiple*x for x in t)


def tuple_add(t: Tuple, addition: int) -> Tuple:
    return tuple(x+addition for x in t)


def get_all_products() -> list:
    return list(product([ShapeType.CORNER, ShapeType.LINE, ShapeType.NUB, ShapeType.BLANK], repeat=4))

def filter(unfiltered: list) -> list:
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

    return  apply_filter_line(apply_filter_corner(unfiltered))

def main():
    prods = filter(get_all_products())
    print(len(prods))

    prods = [(ShapeType.CORNER, ShapeType.BLANK, ShapeType.BLANK, ShapeType.CORNER)]
    for p in prods:
        im = Image.new('RGBA', (PX_PER_TILE, PX_PER_TILE), Color.LIGHT_GREY.value) 
        draw = ImageDraw.Draw(im)
        #draw.arc(((-100, -100), (100,100)), 0, 90, fill=(255, 255, 0, 128), width=12)

        tile = Tile(p)
        for shape in tile.shapes:
            shape.draw(draw)

        #draw.line((left_pt, right_pt), fill=(255, 255, 0, 128), width=12)
        im.show()

if __name__ == "__main__":
    main()
