"""Render a horizontal terminal DNA helix with base-to-binary glyph morphs.

Requires Pillow. No captions or programming-language snippets.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
W, H = 1000, 260
FONT = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 20)
SEQUENCE = 'ATGCGTACGATTCGAGCTACGGTACATGCTAGCTACG'
COMPLEMENT = dict(A='T', T='A', C='G', G='C')
STEM = 'terminal-helix'

def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

glyphs = {}
for char in 'ATCG01':
    glyph = Image.new('L', (24, 28))
    ImageDraw.Draw(glyph).text((12, 14), char, font=FONT, fill=255, anchor='mm')
    glyphs[char] = glyph

frames = []
for frame in range(120):
    t = frame/120
    im = Image.new('RGB', (W,H), 'black')
    d = ImageDraw.Draw(im)
    points = []
    for j, base in enumerate(SEQUENCE):
        x = 60 + j*880/(len(SEQUENCE)-1)
        angle = j/(len(SEQUENCE)-1)*math.pi*5 + t*math.tau
        y = 76*math.sin(angle)
        z = math.cos(angle)
        pair = [(base, H/2+y, z), (COMPLEMENT[base], H/2-y, -z)]
        low, high = sorted((H/2+y,H/2-y))
        for dot_y in range(int(low)+20, int(high)-13, 10):
            d.point((round(x),dot_y), fill=(70,70,70))
        for strand, (letter, yy, depth) in enumerate(pair):
            delay = .10*j/(len(SEQUENCE)-1)
            p = (t-delay) % 1
            morph = smooth((p-.18)/.09)*(1-smooth((p-.65)/.09))
            bit = str((j+strand)%2)
            mask = Image.blend(glyphs[letter],glyphs[bit],morph)
            shade = round(155+100*(depth+1)/2)
            points.append((depth,round(x)-12,round(yy)-14,mask,shade))
    for depth,x,y,mask,shade in sorted(points,key=lambda item:item[0]):
        d.rectangle((x,y,x+23,y+27), fill='black')
        im.paste((shade,shade,shade),(x,y),mask)
    frames.append(im)

frames[0].save(OUT/f'{STEM}-poster.png')
frames[0].save(OUT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True,disposal=2)
sheet = Image.new('RGB',(W,H*3))
for k,i in enumerate((0,48,100)):
    sheet.paste(frames[i],(0,k*H))
sheet.save(OUT/'preview.png')
print(f'Rendered {len(frames)} frames; GIF: {(OUT / f"{STEM}.gif").stat().st_size:,} bytes')
