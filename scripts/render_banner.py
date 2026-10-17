"""Render an ouroboros-like terminal DNA loop with base-to-binary glyph morphs.

Requires Pillow. No captions or programming-language snippets.
"""
from pathlib import Path
import math
import colorsys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
W, H = 1000, 400
FONT = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 18)
SEQUENCE = 'ATGCGTACGATTCGAGCTACGGTACATGCTAGCTACGATCGTACGATGC'
COMPLEMENT = dict(A='T', T='A', C='G', G='C')
STEM = 'ouroboros-sf'
BASE_COLORS = {
    'A': (90, 245, 182),
    'T': (255, 116, 151),
    'C': (103, 185, 255),
    'G': (255, 211, 104),
}

def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

glyphs = {}
for char in 'ATCG01':
    glyph = Image.new('L', (16, 20))
    ImageDraw.Draw(glyph).text((8, 10), char, font=FONT, fill=255, anchor='mm')
    glyphs[char] = glyph

frames = []
for frame in range(240):
    # One rotation every 16.8 seconds; two base/binary cycles per rotation.
    t = frame/240
    im = Image.new('RGB', (W,H), 'black')
    d = ImageDraw.Draw(im)
    points = []
    for j, base in enumerate(SEQUENCE):
        theta = j/len(SEQUENCE)*math.tau - math.pi/2 + t*math.tau
        twist = j/len(SEQUENCE)*math.tau*4 + t*math.tau
        offset = 35*math.sin(twist)
        z = math.cos(twist)
        pair = [(base, 136+offset, z), (COMPLEMENT[base], 136-offset, -z)]
        # The two backbones close into an endless ring, with radial rungs.
        low, high = sorted((136+offset,136-offset))
        for radius in range(int(low)+12, int(high)-10, 6):
            xx = round(W/2+radius*math.cos(theta))
            yy = round(H/2+radius*math.sin(theta))
            d.rectangle((xx,yy,xx+1,yy+1), fill=(155,155,155))
        for strand, (letter, radius, depth) in enumerate(pair):
            x = W/2+radius*math.cos(theta)
            yy = H/2+radius*math.sin(theta)
            delay = .10*j/(len(SEQUENCE)-1)
            p = (2*t-delay) % 1
            morph = smooth((p-.18)/.09)*(1-smooth((p-.65)/.09))
            bit = str((j+strand)%2)
            mask = Image.blend(glyphs[letter],glyphs[bit],morph)
            # Base identity has its own color; binary shifts through a
            # continuous spectrum, blended in sync with the glyph morph.
            binary_color = tuple(255*c for c in colorsys.hsv_to_rgb(
                (t+j/len(SEQUENCE)+strand*.18) % 1, .58, 1))
            brightness = .72+.28*(depth+1)/2
            color = tuple(round((a*(1-morph)+b*morph)*brightness)
                          for a,b in zip(BASE_COLORS[letter],binary_color))
            points.append((depth,round(x)-8,round(yy)-10,mask,color))
    for depth,x,y,mask,color in sorted(points,key=lambda item:item[0]):
        d.rectangle((x,y,x+15,y+19), fill='black')
        im.paste(color,(x,y),mask)
    frames.append(im)

frames[0].save(OUT/f'{STEM}-poster.png')
frames[0].save(OUT/f'{STEM}.gif',save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True,disposal=2)
sheet = Image.new('RGB',(W,H*3))
for k,i in enumerate((0,60,120)):
    sheet.paste(frames[i],(0,k*H))
sheet.save(OUT/'preview.png')
print(f'Rendered {len(frames)} frames; GIF: {(OUT / f"{STEM}.gif").stat().st_size:,} bytes')
