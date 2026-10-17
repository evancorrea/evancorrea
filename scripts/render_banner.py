"""Render the profile's seamless DNA/code loop. Requires Pillow."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
W, H = 1000, 320
BG = '#0d1117'
CYAN, PURPLE = (91, 225, 230), (179, 149, 255)
FONT = '/System/Library/Fonts/Menlo.ttc'
SANS = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(size, path=FONT):
    return ImageFont.truetype(path, size)
def mix(a, b, t):
    return a + (b-a)*t
def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)
def color(rgb, opacity):
    return tuple(int(mix(v, c, opacity)) for v,c in zip((13,17,23),rgb))

frames = []
for frame in range(120):
    t = frame / 120
    # Hold both forms briefly; interpolate in each direction without a jump.
    morph = smooth((t-.16)/.20) * (1-smooth((t-.65)/.20))
    im = Image.new('RGB', (W,H), BG)
    d = ImageDraw.Draw(im)
    for x in range(24,W,24):
        for y in range(24,H,24):
            d.point((x,y), fill='#19212c')
    d.rounded_rectangle((1,1,W-2,H-2),radius=18,outline='#293342',width=1)
    d.text((38,35),'EVAN CORREA / FIELD NOTES',font=font(12),fill='#8b949e')
    d.text((35,87),'Life, written in code.',font=font(35,BOLD),fill='#f0f3f7')
    d.text((38,143),'AI × biology',font=font(21,SANS),fill=CYAN)
    d.text((38,180),'RNA regulation · learning systems',font=font(15,SANS),fill='#adb8c7')
    d.text((38,204),'biosecurity · strange loops',font=font(15,SANS),fill='#adb8c7')
    d.line((38,263,460,263),fill='#293342')
    d.text((38,279),'SEQUENCE → COMPUTATION → SEQUENCE',font=font(11),fill='#8b949e')
    # Right-hand field: two rotating backbones become two columns of code.
    cx, top, step, n = 745, 54, 8.3, 25
    points = [[],[]]
    for strand in range(2):
        for j in range(n):
            a = j*.39 + 2*math.pi*t + strand*math.pi
            x = mix(cx+91*math.sin(a),cx+(-143 if strand==0 else 143),morph)
            y = top+j*step
            z = math.cos(a)
            points[strand].append((x,y,z))
    for j in range(0,n,2):
        a,b=points[0][j],points[1][j]
        d.line((a[0],a[1],b[0],b[1]),fill=color((100,132,159),.45*(1-morph)),width=2)
    for s, rgb in enumerate((CYAN,PURPLE)):
        if morph < .995:
            for j in range(n-1):
                a,b = points[s][j],points[s][j+1]
                d.line((a[0],a[1],b[0],b[1]),fill=color(rgb,(.55+.22*a[2])*(1-morph)),width=3)
        for j,(x,y,z) in enumerate(points[s]):
            r = 2.5 + (z+1)*.65
            d.ellipse((x-r,y-r,x+r,y+r),fill=color(rgb,.55+.23*z))
    code = ['def transcribe(dna):', '    rna = dna.replace(', '        "T", "U"', '    )', '    return rna', '', 'while curious:', '    explore()']
    if morph > .01:
        for j,line in enumerate(code):
            d.text((630,67+j*22),line,font=font(14),fill=color(CYAN if j<5 else PURPLE,morph))
    label='DNA / DOUBLE HELIX' if morph<.5 else 'CODE / TRANSCRIPTION'
    d.text((620,279),label,font=font(11),fill='#8b949e')
    d.ellipse((933,281,939,287),fill=CYAN)
    frames.append(im)

frames[0].save(OUT/'dna-code-poster.png')
frames[0].save(OUT/'dna-code.gif',save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True,disposal=2)
# A contact sheet makes the transition easy to inspect without playing a GIF.
sheet = Image.new('RGB',(W,H*3))
for k,i in enumerate((0,48,100)):
    sheet.paste(frames[i],(0,k*H))
sheet.save(OUT/'preview.png')
print(f'Rendered {len(frames)} frames; GIF: {(OUT / "dna-code.gif").stat().st_size:,} bytes')
