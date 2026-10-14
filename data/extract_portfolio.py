"""Extract project photos from the portfolio PDF into assets/projects/<slug>/.
Usage: python3 data/extract_portfolio.py path/to/Portfolio.pdf
Writes NN.webp (max 1600px) + NN-t.webp (thumb, 640px) and data/photos.json."""
import sys, os, io, json, hashlib
import pymupdf as fitz
from PIL import Image, ImageStat, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {  # slug: (first page, last page)
 'lemon-restaurant': (8, 11), 'wox-palestine': (12, 13), 'patisserie-yvonne': (14, 14),
 'sobh-w-masa-cafe-bakery': (15, 15), 'locanda-farah-boutique-hotel': (16, 18), 'locanda-farah-bar': (19, 19),
 'ramallah-federation-center': (20, 21), 'edward-said-conservatory-of-music': (22, 22),
 'french-german-cultural-center': (23, 25), 'palestine-cinema-days-festival': (26, 27),
 'hyundai-mopar-visitor-center': (28, 29), 'la-vanda-bridal-store': (30, 31), 'al-amani-center': (32, 34),
 'med-dentistry-clinic': (35, 35), 'dr-adel-asfour-clinic': (36, 39), 'dr-salim-basem-clinic': (40, 40),
 'userpilot-ramallah': (41, 43), 'oxfam-ramallah': (44, 46), 'bluemina-ramallah': (47, 48), 'qcom-ramallah': (49, 52),
 'asharq-news-ramallah': (53, 57), 'bloomberg-news-jerusalem': (58, 59), 'sa-apartment': (60, 61), 'sd-villa': (62, 65),
 'downtown-studios': (66, 73), 'sk-rooftop': (74, 81), 'mm-apartment': (82, 82), '_workshops': (83, 86),
}

def orient(im, m):
    if abs(m.a) >= abs(m.b):
        if m.a < 0: im = ImageOps.mirror(im)
        if m.d < 0: im = ImageOps.flip(im)
    else:
        im = im.transpose(Image.TRANSPOSE)
        if m.c < 0: im = ImageOps.mirror(im)
        if m.b < 0: im = ImageOps.flip(im)
    return im

def is_photo(im):
    if min(im.size) < 450: return False
    st = ImageStat.Stat(im.convert('L').resize((64, 64)))
    return st.stddev[0] > 18 and 15 < st.mean[0] < 245   # skips flat black/white graphics

def main(pdf):
    doc = fitz.open(pdf); seen = set(); manifest = {}
    for slug, (a, b) in PAGES.items():
        out = os.path.join(ROOT, 'assets', 'projects', slug); os.makedirs(out, exist_ok=True)
        items = []
        for pno in range(a, b + 1):
            page = doc[pno - 1]
            placed = []
            for img in page.get_images(full=True):
                xref = img[0]
                for rect, m in page.get_image_rects(xref, transform=True):
                    placed.append((rect.y0, rect.x0, xref, m))
            for _, _, xref, m in sorted(placed):          # reading order: top-to-bottom, left-to-right
                raw = doc.extract_image(xref)
                h = hashlib.md5(raw['image']).hexdigest()
                if h in seen: continue
                im = Image.open(io.BytesIO(raw['image']))
                if im.mode == 'CMYK' and raw.get('ext') == 'jpeg': im = ImageOps.invert(im.convert('RGB')) if False else im.convert('RGB')
                im = im.convert('RGB')
                if not is_photo(im): continue
                seen.add(h)
                im = orient(im, m)
                n = len(items) + 1
                full = im.copy(); full.thumbnail((1600, 1600), Image.LANCZOS)
                full.save(os.path.join(out, f'{n:02d}.webp'), 'WEBP', quality=78, method=6)
                th = im.copy(); th.thumbnail((640, 640), Image.LANCZOS)
                th.save(os.path.join(out, f'{n:02d}-t.webp'), 'WEBP', quality=72, method=6)
                items.append({'f': f'{n:02d}', 'w': full.width, 'h': full.height, 'tw': th.width, 'th': th.height, 'page': pno})
        manifest[slug] = items
        print(slug, len(items))
    json.dump(manifest, open(os.path.join(ROOT, 'data', 'photos.json'), 'w'), indent=1)

if __name__ == '__main__':
    main(sys.argv[1])
