"""Builds the Paragon logo set as outlined SVGs (no font dependency)."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FD = os.path.join(os.path.dirname(__file__), 'node_modules/@fontsource/playfair-display/files/')
OUT = os.path.join(os.path.dirname(__file__), 'out'); os.makedirs(OUT, exist_ok=True)
REG = TTFont(FD + 'playfair-display-latin-500-normal.woff2')
BOLD = TTFont(FD + 'playfair-display-latin-700-normal.woff2')
ITA = TTFont(FD + 'playfair-display-latin-400-italic.woff2')

def text_path(font, text, size, x0, baseline, tracking=0.0, skip=()):
    """Return (svg path d, advance-end x, list of glyph boxes). y-down coordinates."""
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font['head'].unitsPerEm
    s = size / upm; x = x0; ds = []; boxes = []
    for i, ch in enumerate(text):
        gname = cmap[ord(ch)]; g = gs[gname]
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, x, baseline))
        bp = BoundsPen(gs); g.draw(bp)
        xmin, ymin, xmax, ymax = bp.bounds or (0, 0, g.width, 0)
        boxes.append((x + xmin * s, baseline - ymax * s, x + xmax * s, baseline - ymin * s))
        if i not in skip:
            g.draw(tp); ds.append(pen.getCommands())
        x += g.width * s + (tracking * size if i < len(text) - 1 else 0)
    return " ".join(ds), x, boxes

def glyph_box(font, ch, size):
    gs = font.getGlyphSet(); g = gs[font.getBestCmap()[ord(ch)]]; bp = BoundsPen(gs); g.draw(bp)
    s = size / font['head'].unitsPerEm; return [v * s for v in bp.bounds], g.width * s

def build(ink, accent, tag_color, with_tagline=True, pad=8, font=None, stroke=3.2):
    font = font or REG
    size = 100
    base = 100  # baseline y
    # Wordmark: draw "PARACON" (the C becomes our G), hammer added as the G's bar + stem
    word = "PARACON"
    d_word, x_end, boxes = text_path(font, word, size, pad, base, tracking=0.16)
    cap_top = min(b[1] for b in boxes); x_start = boxes[0][0]; x_stop = boxes[-1][2]

    # Hammer in the "C" -> G
    cx0, cy0, cx1, cy1 = boxes[4]
    w = cx1 - cx0; h = cy1 - cy0
    head_y = cy0 + h * 0.47            # top of hammer head
    hh = h * 0.12                      # head thickness
    face_x = cx1 + w * 0.03            # striking face, flush with the G's open edge
    hl = w * 0.66                      # head length incl. claw
    neck_x = face_x - w * 0.36
    claw_tip_x = face_x - hl
    hx0 = face_x - w * 0.24; hx1 = face_x - w * 0.12   # handle
    hammer = (
        # head: flat top, square face, claw sweeping down-left
        f"M{face_x:.2f},{head_y - hh*0.15:.2f} V{head_y + hh*1.15:.2f} H{neck_x:.2f} "
        f"C{neck_x - w*0.10:.2f},{head_y + hh*1.05:.2f} {claw_tip_x + w*0.06:.2f},{head_y + hh*1.4:.2f} {claw_tip_x:.2f},{head_y + hh*2.3:.2f} "
        f"C{claw_tip_x + w*0.04:.2f},{head_y + hh*0.6:.2f} {neck_x - w*0.12:.2f},{head_y:.2f} {neck_x:.2f},{head_y:.2f} "
        f"H{face_x - w*0.04:.2f} V{head_y - hh*0.15:.2f} Z "
        # handle = the G's spur
        f"M{hx0:.2f},{head_y + hh:.2f} H{hx1:.2f} V{cy0 + h*0.88:.2f} "
        f"Q{(hx0+hx1)/2:.2f},{cy0 + h*0.93:.2f} {hx0:.2f},{cy0 + h*0.88:.2f} Z"
    )

    # Key underline
    key_y = base + 16
    ring_r = 6.5 + (stroke - 3.2)
    key_x0 = x_start - 2; key_x1 = x_stop + 2
    key = (
        f'<path d="M{key_x0:.2f},{key_y:.2f} H{key_x1 - ring_r*2:.2f}" stroke="{accent}" stroke-width="{stroke}" fill="none"/>'
        f'<circle cx="{key_x1 - ring_r:.2f}" cy="{key_y:.2f}" r="{ring_r - stroke/2:.2f}" stroke="{accent}" stroke-width="{stroke}" fill="none"/>'
        f'<rect x="{key_x0:.2f}" y="{key_y:.2f}" width="{7 + (stroke-3.2)*1.5:.1f}" height="17" fill="{accent}"/>'
        f'<rect x="{key_x0 + 12 + (stroke-3.2)*2:.2f}" y="{key_y:.2f}" width="{7 + (stroke-3.2)*1.5:.1f}" height="12" fill="{accent}"/>'
    )

    parts = [f'<path d="{d_word}" fill="{ink}"/>', f'<path d="{hammer}" fill="{accent}"/>', key]
    height = key_y + 20
    if with_tagline:
        tag = "A MODEL OF EXCELLENCE"; tsize = 19
        # measure, then centre under the wordmark (shifted right of the key teeth)
        _, tw_end, tb = text_path(ITA, tag, tsize, 0, 0, tracking=0.22)
        tw = tb[-1][2] - tb[0][0]
        tx = (key_x0 + 24 + key_x1 - ring_r*2) / 2 - tw / 2
        ty = key_y + 26
        d_tag, _, _ = text_path(ITA, tag, tsize, tx, ty, tracking=0.22)
        parts.append(f'<path d="{d_tag}" fill="{tag_color}"/>')
        height = ty + 8
    width = key_x1 + pad
    vb_y = cap_top - pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {vb_y:.1f} {width:.1f} {height - vb_y + pad/2:.1f}" '
            f'role="img" aria-label="Paragon — A Model of Excellence">' + "".join(parts) + '</svg>')

def build_icon(bg, fg, accent):
    size = 96
    box, adv = glyph_box(REG, 'P', size)
    xmin, ymin, xmax, ymax = box
    gw = xmax - xmin
    x = 64 - gw/2 - xmin; base = 84
    d, _, _ = text_path(REG, 'P', size, x, base)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="Paragon">'
            f'<rect width="128" height="128" rx="28" fill="{bg}"/>'
            f'<path d="{d}" fill="{fg}"/>'
            f'<path d="M24 100 H95" stroke="{accent}" stroke-width="5" fill="none"/>'
            f'<circle cx="101" cy="100" r="6" stroke="{accent}" stroke-width="5" fill="none"/>'
            f'<rect x="24" y="100" width="7" height="12" fill="{accent}"/><rect x="35" y="100" width="7" height="8" fill="{accent}"/>'
            '</svg>')

TEAL = '#18AFAB'; INK = '#111827'; GOLD = '#B98A3E'
files = {
  'paragon-logo.svg': build(INK, TEAL, '#4B5563'),
  'paragon-logo-light.svg': build('#FFFFFF', TEAL, 'rgba(255,255,255,0.72)'),
  'paragon-logo-mark.svg': build(INK, TEAL, '#4B5563', with_tagline=False, font=BOLD, stroke=6),
  'paragon-logo-mark-light.svg': build('#FFFFFF', TEAL, '#fff', with_tagline=False, font=BOLD, stroke=6),
  'paragon-logo-gold.svg': build('#14213D', GOLD, '#14213D'),
  'paragon-icon.svg': build_icon('#0F0F10', '#FFFFFF', TEAL),
}
for n, s in files.items():
    open(os.path.join(OUT, n), 'w').write(s)
print("done", list(files))
