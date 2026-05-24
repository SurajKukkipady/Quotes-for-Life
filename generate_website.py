#!/usr/bin/env python3
"""
generate_website.py

Read `quotes.json` and generate a static `index.html` that embeds the images and quotes.

Usage:
  python generate_website.py            # writes ./index.html from ./quotes.json
  python generate_website.py -i src.json -o out.html

Place your uploaded quote images in the `images/` directory and update `quotes.json` accordingly.
"""
import json
import argparse
from pathlib import Path

TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Quotes Gallery</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f7f7f7;color:#111}
    header{background:#222;color:#fff;padding:1rem;text-align:center}
    .container{max-width:1000px;margin:2rem auto;padding:0 1rem}
    .filters{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.25rem}
    .filter-button{border:1px solid rgba(255,255,255,.55);background:#fff;color:#222;padding:.5rem .85rem;border-radius:999px;cursor:pointer;transition:background .2s,border-color .2s,color .2s}
    .filter-button.active,.filter-button:hover{background:#222;color:#fff;border-color:#222}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;align-items:start}
    .card{background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,.08);display:flex;flex-direction:column}
    .card.hidden{display:none}
    .card img{width:100%;height:auto;display:block;object-fit:cover;transition:transform .25s ease}
    .card.portrait img{object-fit:contain}
    .card:hover img{transform:scale(1.02)}
    .caption{padding:.75rem}
    .category{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#888;margin:0 0 .5rem;font-weight:700}
    .quote{font-size:0.95rem;margin:0 0 .5rem}
    .author{font-size:.85rem;color:#555}
  </style>
</head>
<body>
  <header>
    <h1 style="margin:0">Quotes Gallery</h1>
  </header>
  <main class="container">
    <div id="filters" class="filters"></div>
    <div class="grid">
      {cards}
    </div>
  </main>
  <script>
    const cards = Array.from(document.querySelectorAll('.card'));
    const filters = document.getElementById('filters');
    const categories = Array.from(new Set(cards.map(card => card.dataset.category).filter(Boolean)));

    function setActiveFilter(button) {
      document.querySelectorAll('.filter-button').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
    }

    function filterCategory(category) {
      cards.forEach(card => {
        card.classList.toggle('hidden', category !== 'All' && card.dataset.category !== category);
      });
    }

    function createButton(name, active = false) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'filter-button' + (active ? ' active' : '');
      button.textContent = name;
      button.addEventListener('click', () => {
        setActiveFilter(button);
        filterCategory(name);
      });
      return button;
    }

    filters.appendChild(createButton('All', true));
    categories.forEach(category => filters.appendChild(createButton(category)));

    document.querySelectorAll('.card img').forEach(img => {
      const card = img.closest('.card');
      function updateCard() {
        if (!card) return;
        const ratio = img.naturalWidth / img.naturalHeight;
        card.classList.toggle('landscape', ratio >= 1.2);
        card.classList.toggle('portrait', ratio < 1.2);
      }
      if (img.complete) {
        updateCard();
      } else {
        img.addEventListener('load', updateCard);
      }
    });
  </script>
</body>
</html>
'''

CARD = '''<article class="card" data-category="{category}">
  <img src="{image}" alt="{alt}" />
  <div class="caption">
    <p class="category">{category}</p>
    <p class="quote">{quote}</p>
    <p class="author">{author}</p>
  </div>
</article>'''

def build_cards(quotes):
    parts = []
    for q in quotes:
        img = q.get('image') or q.get('img') or q.get('image_path') or ''
        quote = (q.get('quote') or q.get('text') or '').replace('<','&lt;').replace('>','&gt;')
        author = q.get('author','')
        category = q.get('category','General')
        alt = quote[:80]
        parts.append(CARD.format(image=img, alt=alt, quote=quote, author=author, category=category))
    return '\n'.join(parts)

def main():
    p = argparse.ArgumentParser(description='Generate static index.html from quotes.json')
    p.add_argument('-i','--input',default='quotes.json')
    p.add_argument('-o','--output',default='index.html')
    args = p.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f'Input file not found: {inp}')
        return

    data = json.loads(inp.read_text(encoding='utf-8'))
    quotes = data.get('quotes') if isinstance(data, dict) and 'quotes' in data else data
    cards = build_cards(quotes)
    out_html = TEMPLATE.replace('{cards}', cards)
    Path(args.output).write_text(out_html, encoding='utf-8')
    print(f'Wrote {args.output} ({len(quotes)} quotes)')

if __name__ == '__main__':
    main()
