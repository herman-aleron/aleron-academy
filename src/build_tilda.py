"""Build Tilda T123 versions of both landings.
Output per page (webinar, courses) in /mnt/user-data/outputs/tilda/<page>/:
  T123_<page>_inline.html  - one block, photos embedded (paste-and-go, heavy)
  T123_<page>.html         - one block, photos as URLs: replace __IMG_BASE__ after uploading images/
  images/                  - WebP photos for the light version
"""
import re, os, shutil, sys, base64, io
from PIL import Image, ImageOps
sys.path.insert(0, '/home/claude')

P1 = '/home/claude/photos/Media Content/'; P2 = '/mnt/user-data/uploads/Marketing/Inputs/Site photos/'
OUT = '/mnt/user-data/outputs/tilda/'
SCOPE = '#aleron-lp'

def src_path(f): return (P1 if os.path.exists(P1 + f) else P2) + f

def webp(f, w, q, dest):
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB'); im.thumbnail((w, w)); im.save(dest, 'WEBP', quality=q, method=6)

def datauri(path):
    b = open(path, 'rb').read(); return 'data:image/webp;base64,' + base64.b64encode(b).decode()

# ---------- CSS scoping ----------
def scope_selector(sel):
    sel = sel.strip()
    if not sel: return sel
    if sel in (':root', 'html', 'body'): return SCOPE
    if sel == '*': return f'{SCOPE},{SCOPE} *'
    for pre in ('html ', 'body '):
        if sel.startswith(pre): return SCOPE + ' ' + sel[len(pre):]
    return f'{SCOPE} {sel}'

def split_commas(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur); return out

def scope_css(css):
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0: out.append(css[i:]); break
        head = css[i:j]
        # find matching brace
        depth, k = 1, j + 1
        while depth and k < n:
            if css[k] == '{': depth += 1
            elif css[k] == '}': depth -= 1
            k += 1
        body = css[j + 1:k - 1]
        h = head.strip()
        if h.startswith('@media') or h.startswith('@supports'):
            out.append(head + '{' + scope_css(body) + '}')
        elif h.startswith('@'):
            out.append(head + '{' + body + '}')
        else:
            lead = head[:len(head) - len(head.lstrip())]
            out.append(lead + ','.join(scope_selector(s) for s in split_commas(h)) + '{' + body + '}')
        i = k
    return ''.join(out)

# ---------- page transforms ----------
FIT = r'''
/* ===== Tilda: keep the page clear of the site header =====
   The site header (#t-header) draws its menu over the top of the next block.
   Measure how far it reaches into this block and pad the first section by that much. */
(() => {
  const lp = document.getElementById('aleron-lp'); if (!lp) return;
  function fit() {
    if (scrollY > 50) return;
    const hdr = document.getElementById('t-header');
    if (!hdr) { lp.style.setProperty('--site-head', '0px'); return; }
    const lpTop = lp.getBoundingClientRect().top + scrollY;
    let bottom = 0;
    hdr.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
      const r = el.getBoundingClientRect();
      if (!r.height || r.height > 300 || r.right <= 0 || r.left >= innerWidth) return;
      bottom = Math.max(bottom, r.bottom + scrollY);
    });
    lp.style.setProperty('--site-head', Math.max(0, Math.round(bottom - lpTop)) + 'px');
  }
  fit(); setTimeout(fit, 400); setTimeout(fit, 1500);
  addEventListener('load', fit); addEventListener('resize', fit);
})();
'''
CONSENT_START = '/* ===== Meta Pixel, loaded only after consent ===== */'
def strip_consent(js):
    a = js.index(CONSENT_START)
    b = js.index("  open.onclick = () => { box.hidden = false; };\n", a) + len("  open.onclick = () => { box.hidden = false; };\n")
    return js[:a] + "/* ===== Tilda: Meta Pixel (1476822027723349) is already loaded by the site, so this block\n   does not load it again and shows no cookie banner. Events go to window.fbq via px(). ===== */\n(() => {\n" + js[b:]

def build(page, src, spec):
    s = open(src, encoding='utf-8').read()
    css = s[s.index('<style>') + 7:s.index('</style>')]
    body = s[s.index('<body>') + 6:s.rindex('</body>')]
    # split body into markup and scripts
    first_script = body.index('<script>')
    html, scripts = body[:first_script], body[first_script:]
    html = re.sub(r'<header class="bar">.*?</header>\n?', '', html, count=1, flags=re.S)
    html = re.sub(r'<div class="cookie" id="cookie".*?</div>\n</div>\n', '', html, count=1, flags=re.S)
    html = re.sub(r'( · )?<button class="cookie-link" type="button" id="ck-open" hidden>[^<]*</button>', '', html)
    scripts = strip_consent(scripts)
    scripts = scripts[:scripts.rindex('</script>')] + FIT + scripts[scripts.rindex('</script>'):]
    assert 'ck-yes' not in html and 'id="cookie"' not in html and '<header class="bar"' not in html
    extra_css = (f'\n{SCOPE}{{display:block;position:relative;text-align:left;-webkit-font-smoothing:antialiased}}'
                 f'{SCOPE} section.hero{{padding-top:var(--site-head,0px)!important}}{SCOPE} [id]{{scroll-margin-top:calc(var(--site-head,0px) + 20px)}}'
                 f'{SCOPE} input,{SCOPE} select,{SCOPE} textarea,{SCOPE} button{{font-family:Arial,sans-serif}}\n')
    reset = ','.join(f'{SCOPE} {t}' for t in 'h1 h2 h3 h4 p li a span b strong small label blockquote figcaption summary dt dd'.split()) + '{font-family:inherit;color:inherit}\n'
    scoped = reset + scope_css(css) + extra_css
    # images
    d = OUT + page + '/'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d + 'images')
    keys = set(re.findall(r'\{\{(\w+)\}\}', html + scoped))
    light, inline = html + '\u0000' + scoped, html + '\u0000' + scoped
    for k in sorted(keys):
        f, w, q = spec[k]
        name = k.lower() + '.webp'
        if f.startswith('/'): webp(f, w, q, d + 'images/' + name)
        else: webp(src_path(f), w, q, d + 'images/' + name)
        light = light.replace('{{' + k + '}}', '__IMG_BASE__' + name)
        inline = inline.replace('{{' + k + '}}', datauri(d + 'images/' + name))
    head = (f'<!-- Aleron Academy - {page} landing for Tilda block T123 (Embed HTML code).\n'
            '     Paste the whole file into ONE T123 block on an empty page, then publish.\n'
            '     Pixel: uses the Meta Pixel the site already loads; no second pixel, no cookie banner. -->\n')
    for variant, content in (('', light), ('_inline', inline)):
        h, c = content.split('\u0000')
        out = head + f'<style>\n{c}\n</style>\n<div id="aleron-lp">\n{h}</div>\n{scripts}\n'
        open(d + f'T123_{page}{variant}.html', 'w', encoding='utf-8').write(out)
    for v in ('', '_inline'):
        print(page, v or '_light', os.path.getsize(d + f'T123_{page}{v}.html') // 1024, 'KB')
    print(page, 'images', len(os.listdir(d + 'images')), sum(os.path.getsize(d + 'images/' + x) for x in os.listdir(d + 'images')) // 1024, 'KB')

WEB = {'HERO': ('IMG_6226.JPG', 1600, 72), 'G1': ('IMG_6205.JPG', 640, 70), 'G2': ('IMG_6206.JPG', 640, 70), 'G3': ('IMG_6207.JPG', 640, 70),
       'G4': ('IMG_6227.JPG', 640, 70), 'G5': ('IMG_6209.JPG', 640, 70), 'G6': ('IMG_6262.PNG', 640, 70), 'W1': ('IMG_6204.JPG', 600, 74),
       'W2': ('IMG_6214.JPG', 600, 74), 'W3': ('IMG_6224.JPG', 600, 74), 'WHY': ('IMG_6228.JPG', 700, 74), 'AG': ('IMG_6216.JPG', 700, 74),
       'G7': ('IMG_6213.JPG', 640, 70), 'G8': ('IMG_6234.JPG', 640, 70), 'G9': ('IMG_6219.JPG', 640, 70), 'G10': ('IMG_6242.JPG', 640, 70),
       'G11': ('IMG_6261.PNG', 640, 70), 'G12': ('IMG_6244.JPG', 640, 70), 'R1': ('IMG_6264.PNG', 560, 70), 'R2': ('IMG_6233.JPG', 560, 70),
       'R3': ('IMG_6229.JPG', 560, 70), 'FAQ': ('IMG_6236.JPG', 640, 70), 'BGPAY': ('IMG_6238.JPG', 1280, 60), 'BGBONUS': ('IMG_6241.JPG', 1280, 60),
       'BGREG': ('IMG_6220.JPG', 1280, 60), 'LOGO': ('/home/claude/lp/img0.png', 400, 90), 'CERT': ('/home/claude/lp/cert.jpg', 900, 80)}
CRS = {'LOGO': ('/home/claude/lp/img0.png', 400, 90), 'HERO': ('IMG_6238.JPG', 1600, 72), 'WHY': ('IMG_6228.JPG', 700, 74),
       'W1': ('IMG_6204.JPG', 600, 74), 'W2': ('IMG_6214.JPG', 600, 74), 'W3': ('IMG_6224.JPG', 600, 74),
       'CERT': ('/home/claude/cert/cert_theory.png', 700, 82), 'DIPLOMA': ('/home/claude/cert/cert_diploma.png', 700, 82),
       'G1': ('IMG_6219.JPG', 640, 70), 'G2': ('IMG_6206.JPG', 640, 70), 'G3': ('IMG_6207.JPG', 640, 70), 'G4': ('IMG_6234.JPG', 640, 70),
       'G5': ('IMG_6209.JPG', 640, 70), 'G6': ('IMG_6261.PNG', 640, 70), 'BGTEAM': ('IMG_6238.JPG', 1280, 60), 'BGFORM': ('IMG_6220.JPG', 1280, 60),
       'FAQ': ('IMG_6236.JPG', 640, 70), 'NVQ': ('/home/claude/cert/nvq_sample.png', 700, 82)}
build('webinar', '/home/claude/lp/page.html', WEB)
build('courses', '/home/claude/course/page.html', CRS)
