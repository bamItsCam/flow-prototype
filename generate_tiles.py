#!/usr/local/bin/python3

# A = corner
# B = line
# C = nub
# D = blank

from itertools import product
from PIL import Image, ImageDraw

top_index=0
right_index=1
bot_index=2
left_index=3

top_pt=(100, 0)
right_pt=(200, 100)
bot_pt=(100, 200)
left_pt=(0, 100)

def get_all_products() -> list:
    return list(product(["A", "B", "C", "D"], repeat=4))

def filter(unfiltered: list) -> list:
    def apply_filter_a(unfiltered: list) -> list:
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-3-6-9-12-15___________option-0_____989780977179845392647
        filtered = []
        for p in unfiltered:
            top = p[top_index] == "A"
            right = p[right_index] == "A"
            bot = p[bot_index] == "A"
            left = p[left_index] == "A"
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

    def apply_filter_b(unfiltered: list) -> list:
        # http://www.32x8.com/sop4_____A-B-C-D_____m_0-5-10-15___________option-0_____999782971575855597795
        filtered = []
        for p in unfiltered:
            top = p[top_index] == "B"
            right = p[right_index] == "B"
            bot = p[bot_index] == "B"
            left = p[left_index] == "B"
            if (
                (not top and not right and not bot and not left)
                or (not top and right and not bot and left)
                or (top and not right and bot and not left)
                or (top and right and bot and left)
            ):
                filtered.append(p)
            
        return filtered

    return  apply_filter_b(apply_filter_a(unfiltered))

def main():
    prods = filter(get_all_products())
    for p in prods:
        print(p)
    print(len(prods))

    prods = [('D', 'C', 'D', 'C')]
    for p in prods:
        im = Image.new('RGBA', (200, 200), (216, 216, 216, 255)) 
        draw = ImageDraw.Draw(im)
        draw.arc(((-100, -100), (100,100)), 0, 90, fill=(255, 255, 0, 128), width=12)

        draw.line((left_pt, right_pt), fill=(255, 255, 0, 128), width=12)
        im.show()

if __name__ == "__main__":
    main()
