"""Build the files that Tilda loads live from GitHub Pages.
live/<page>.html = the light T123 block with image URLs pointing to GitHub Pages.
tilda/loader_<page>.html = the short code that goes into the Tilda T123 block once."""
import os
BASE = 'https://herman-aleron.github.io/aleron-academy/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(ROOT, 'live'), exist_ok=True)
LOADER = '''<!-- Aleron Academy - {page} landing, live from GitHub ({repo}).
     Put this code into ONE T123 block on fire-proof.co.uk/{page} and publish once.
     Later changes pushed to GitHub appear on the site within ~10 minutes, no Tilda republish. -->
<div id="aleron-live" style="min-height:70vh"></div>
<script>
(function () {{
  var SRC = '{base}live/{page}.html';
  var box = document.getElementById('aleron-live');
  function fail() {{
    box.style.minHeight = '0';
    box.innerHTML = '<div style="padding:60px 20px;text-align:center;font:16px/1.5 Arial,sans-serif">' +
      'This page did not load. Please refresh, or email <a href="mailto:academy@aleron.co.uk">academy@aleron.co.uk</a>.</div>';
  }}
  fetch(SRC + '?v=' + Math.floor(Date.now() / 300000), {{ cache: 'no-cache' }})
    .then(function (r) {{ if (!r.ok) throw new Error(r.status); return r.text(); }})
    .then(function (html) {{
      var tmp = document.createElement('div');
      tmp.innerHTML = html;
      var scripts = Array.prototype.slice.call(tmp.querySelectorAll('script'));
      scripts.forEach(function (s) {{ s.parentNode.removeChild(s); }});
      var parent = box.parentNode;
      while (tmp.firstChild) parent.insertBefore(tmp.firstChild, box);
      parent.removeChild(box);
      scripts.forEach(function (old) {{
        var s = document.createElement('script');
        s.text = old.textContent;
        document.body.appendChild(s);
      }});
      if (location.hash) {{ var t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }}
    }})
    .catch(fail);
}})();
</script>
'''
for page in ('webinar', 'courses'):
    src = open(os.path.join(ROOT, 'tilda', page, f'T123_{page}.html'), encoding='utf-8').read()
    live = src.replace('__IMG_BASE__', f'{BASE}tilda/{page}/images/')
    open(os.path.join(ROOT, 'live', f'{page}.html'), 'w', encoding='utf-8').write(live)
    open(os.path.join(ROOT, 'tilda', f'loader_{page}.html'), 'w', encoding='utf-8').write(
        LOADER.format(page=page, base=BASE, repo='herman-aleron/aleron-academy'))
    print(page, 'ok')
