#!/usr/bin/env python3
"""Rigenera le pagine del sito Imago Artis Edizioni dai file originali.

Uso:
    python build.py

Legge da assets/sorgenti/pagine-originali/, scrive in ./ e libri/, genera
sitemap.xml, favicon e immagini Open Graph. È idempotente: puoi rilanciarlo.
"""

import glob
import html
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets", "sorgenti", "pagine-originali")
SITE = "https://imagoartisedizioni.it"
EMAIL = "info@imagoartisedizioni.it"
VAT = "03326490780"
GOOGLE_VERIFICATION = "J86MnaHWH8AGKfXeIleb_x-7fKvymelmllWCQOnYLSI"

PAGES = {
    "index.html": {
        "title": "Imago Artis Edizioni — Casa editrice indipendente in Calabria",
        "description": "Casa editrice indipendente di Rossano (CS): volumi sul Codex Purpureus Rossanensis, memoria e territorio calabrese, narrativa e nuovi autori. Scopri il catalogo.",
        "path": "/",
        "image": "og/home.jpg",
    },
    "catalogo.html": {
        "title": "Catalogo libri — Imago Artis Edizioni",
        "description": "Tutte le pubblicazioni di Imago Artis Edizioni: collana Memoria e Territorio, Edizioni di Pregio sul Codex Purpureus e narrativa. Schede, prezzi e acquisto.",
        "path": "/catalogo.html",
        "image": "og/catalogo.jpg",
    },
    "territorio.html": {
        "title": "Il Progetto Memoria — Imago Artis Edizioni",
        "description": "Ristampe storiche e recupero della memoria calabrese: il progetto editoriale di Imago Artis Edizioni tra archivi, introduzioni critiche e Codex Purpureus.",
        "path": "/territorio.html",
        "image": "og/home.jpg",
    },
    "autori.html": {
        "title": "Invia il tuo manoscritto — Imago Artis Edizioni",
        "description": "Linee editoriali, documenti da allegare e come inviare il manoscritto a Imago Artis Edizioni: narrativa, saggistica e ricerca storica del territorio.",
        "path": "/autori.html",
        "image": "og/autori.jpg",
    },
    "chi-siamo.html": {
        "title": "La redazione — Imago Artis Edizioni",
        "description": "Una casa editrice indipendente a Rossano (CS) che pubblica storia, memoria e narrativa del Mezzogiorno, con un'attenzione speciale al Codex Purpureus Rossanensis.",
        "path": "/chi-siamo.html",
        "image": "og/chi-siamo.jpg",
    },
    "contatti.html": {
        "title": "Contatti — Imago Artis Edizioni",
        "description": "Scrivi a Imago Artis Edizioni per ordini, presentazioni o invio di manoscritti. Email, WhatsApp e modulo di contatto. Sede a Rossano (CS), Calabria.",
        "path": "/contatti.html",
        "image": "og/contatti.jpg",
    },
}

BOOKS = {
    "rossano": dict(
        title="Rossano tra storia e bio-bibliografia",
        author="Franco Emilio Carlino",
        price="25,00",
        availability="Immediata",
        cover="01Rossano.webp",
        category="Memoria e Territorio",
    ),
    "mandatoriccio": dict(
        title="Mandatoriccio, storia di un feudo",
        author="Franco Emilio Carlino",
        price="20,00",
        availability="Immediata",
        cover="02Mandatoriccio.webp",
        category="Memoria e Territorio",
    ),
    "scuola": dict(
        title="Scuola: il punto di vista",
        author="Franco Emilio Carlino",
        price="12,00",
        availability="Immediata",
        cover="03Scuola.webp",
        category="Memoria e Territorio",
    ),
    "patire": dict(
        title="Il Patire — Storia e colori di un'antica abbazia",
        author="Franco Emilio Carlino",
        price="13,00",
        availability="Immediata",
        cover="05Patire.webp",
        category="Memoria e Territorio",
    ),
    "universita": dict(
        title="L'Università Popolare di Rossano",
        author="Franco Emilio Carlino",
        price="18,00",
        availability="Immediata",
        cover="06Universita.webp",
        category="Memoria e Territorio",
    ),
    "terra": dict(
        title="La Terra di Mormanno in Calabria Citra nel Viceregno",
        author="Francesco Regina",
        price="8,00",
        availability="Immediata",
        cover="11Terra.webp",
        category="Memoria e Territorio",
    ),
    "tusa": dict(
        title="Tusa dei Desideri",
        author="Gianfranco Labrosciano",
        price="12,00",
        availability="Immediata",
        cover="07Tusa.webp",
        category="Narrativa e Spiritualità",
    ),
    "sonetti": dict(
        title="I Me' Sonetti",
        author="Natale Cutrupi",
        price="12,00",
        availability="Immediata",
        cover="08Sonetti.webp",
        category="Narrativa e Spiritualità",
    ),
    "catechismo": dict(
        title="Il Catechismo del Codex Purpureus Rossanensis",
        author="Giovanni Sapia",
        price="18,00",
        availability="Su richiesta",
        cover="09Catechismo.webp",
        category="Narrativa e Spiritualità",
    ),
    "compassione": dict(
        title="La Compassione dall'alto della Croce",
        author="Antonio di Nardo",
        price="8,00",
        availability="Immediata",
        cover="10Compassione.webp",
        category="Narrativa e Spiritualità",
    ),
    "lettera": dict(
        title="Lettera a mio figlio sulla Politica",
        author="Giandonato Giordano",
        price="10,00",
        availability="Immediata",
        cover="12Lettera.webp",
        category="Narrativa e Spiritualità",
    ),
    "ben": dict(
        title="Il Ben Ch'io vi Trovai",
        author="Coriolano Martirano",
        price="15,00",
        availability="Immediata",
        cover="13Ben.webp",
        category="Narrativa e Spiritualità",
    ),
    "codex": dict(
        title="Il Codex Purpureus Rossanensis",
        author="Franco Emilio Carlino",
        price="18,00",
        availability="Immediata",
        cover="04Codex.webp",
        category="Edizioni di Pregio",
    ),
}

ORG_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Imago Artis Edizioni",
    "url": SITE + "/",
    "logo": SITE + "/logo.png",
    "email": EMAIL,
    "vatID": VAT,
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Rossano",
        "addressRegion": "CS",
        "addressCountry": "IT",
    },
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def text_only(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def image_size(path):
    with Image.open(path) as im:
        return im.size


def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\georgia" + ("bd" if bold else "") + ".ttf",
        r"C:\Windows\Fonts\georgiab.ttf" if bold else r"C:\Windows\Fonts\georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif" + ("-Bold" if bold else "") + ".ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_og():
    """Immagine Open Graph 1200x630 per home e schede libro."""
    out_dir = os.path.join(ROOT, "og")
    os.makedirs(out_dir, exist_ok=True)
    crema = (253, 252, 248)
    bordeaux = (139, 26, 26)
    ink = (28, 25, 23)
    muted = (120, 113, 108)

    def compose(cover_path, title, subtitle, out_name):
        canvas = Image.new("RGB", (1200, 630), crema)
        draw = ImageDraw.Draw(canvas)
        if cover_path and os.path.exists(cover_path):
            with Image.open(cover_path) as cover:
                cover = cover.convert("RGB")
                h = 470
                w = round(cover.width * h / cover.height)
                cover = cover.resize((w, h), Image.LANCZOS)
                canvas.paste(cover, (80, 80))
        x = 80 + (470 * 2 // 3 + 60 if cover_path else 0)
        right = 1200 - 70
        title_font = load_font(50, bold=True)
        small_font = load_font(22)
        label_font = load_font(17, bold=True)
        draw.text((x, 120), "IMAGO ARTIS EDIZIONI", font=label_font, fill=bordeaux)
        y = 175
        for line in wrap(draw, title, title_font, right - x):
            draw.text((x, y), line, font=title_font, fill=ink)
            y += 62
        y += 16
        for line in wrap(draw, subtitle, small_font, right - x):
            draw.text((x, y), line, font=small_font, fill=muted)
            y += 30
        draw.rectangle([80, 570, 140, 574], fill=bordeaux)
        draw.text((160, 560), "imagoartisedizioni.it", font=small_font, fill=muted)
        canvas.save(os.path.join(out_dir, out_name), "JPEG", quality=86, optimize=True)

    compose("04Codex.webp", "Custodi della memoria, editori dell'identità",
            "Codex Purpureus Rossanensis, storia e narrativa del Mezzogiorno", "home.jpg")
    for name in ("catalogo", "autori", "chi-siamo", "contatti"):
        compose("04Codex.webp", {
            "catalogo": "Catalogo editoriale",
            "autori": "Invia il tuo manoscritto",
            "chi-siamo": "La redazione",
            "contatti": "Contattaci",
        }[name], "Imago Artis Edizioni — Rossano, Calabria", name + ".jpg")
    for slug, book in BOOKS.items():
        compose(book["cover"], book["title"], "di " + book["author"], slug + ".jpg")


def seo_block(meta, rel, path, image, jsonld):
    url = SITE + path
    google = (
        f'    <meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">\n'
        if path == "/"
        else ""
    )
    return f"""    <!-- head:seo -->
    <title>{html.escape(meta['title'])}</title>
{google}    <meta name="description" content="{html.escape(meta['description'], quote=True)}">
    <link rel="canonical" href="{url}">
    <meta name="theme-color" content="#8B1A1A">
    <meta property="og:type" content="{'book' if jsonld.get('@type') == 'Book' else 'website'}">
    <meta property="og:site_name" content="Imago Artis Edizioni">
    <meta property="og:locale" content="it_IT">
    <meta property="og:title" content="{html.escape(meta['title'], quote=True)}">
    <meta property="og:description" content="{html.escape(meta['description'], quote=True)}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{SITE}/{image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(meta['title'], quote=True)}">
    <meta name="twitter:description" content="{html.escape(meta['description'], quote=True)}">
    <meta name="twitter:image" content="{SITE}/{image}">
    <link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
    <link rel="icon" href="{rel}favicon-32.png" sizes="32x32">
    <link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
    <link rel="preload" href="{rel}assets/fonts/cormorant-garamond-400-italic-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="{rel}assets/fonts/inter-400-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="{rel}assets/fonts.css">
    <link rel="stylesheet" href="{rel}assets/tailwind.css">
    <link rel="stylesheet" href="{rel}assets/site.css">
    <script src="{rel}assets/site.js" defer></script>
    <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
"""


def add_attr(tag, attr):
    tag = tag.rstrip()
    if tag.endswith("/>"):
        return tag[:-2].rstrip() + " " + attr + ">"
    return tag[:-1].rstrip() + " " + attr + ">"


def add_img_attrs(tag, rel, alt_map):
    src_m = re.search(r'src="([^"]+)"', tag)
    if not src_m:
        return tag
    src = src_m.group(1)
    name = os.path.basename(src)
    if not re.search(r"\balt=", tag):
        alt = alt_map.get(name, "Imago Artis Edizioni")
        tag = add_attr(tag, f'alt="{html.escape(alt, quote=True)}"')
    if "book-img" in tag or "Copertina" in alt_map.get(name, ""):
        if not re.search(r"\bloading=", tag):
            tag = add_attr(tag, 'loading="lazy"')
        if not re.search(r"\bdecoding=", tag):
            tag = add_attr(tag, 'decoding="async"')
    if not re.search(r"\bwidth=|height=", tag):
        local = os.path.join(ROOT, src.replace("../", ""))
        if os.path.exists(local):
            w, h = image_size(local)
            tag = add_attr(tag, f'width="{w}" height="{h}"')
    return tag


def card_price(match):
    """Aggiunge il prezzo nella card del catalogo."""
    card = match.group(0)
    href = re.search(r'href="(?:\.\./)?libri/([a-z]+)\.html"', card)
    if not href or href.group(1) not in BOOKS:
        return card
    book = BOOKS[href.group(1)]
    if "book-price" in card:
        return card
    price = f'<p class="book-price">€ {book["price"]}</p>'
    return card.replace("</a>", "</a>" + price)


def transform_book(name, source):
    book = BOOKS[name]
    rel = "../"
    path = f"/libri/{name}.html"
    meta = {
        "title": book["title"] + " — Imago Artis Edizioni",
        "description": f"{book['title']} di {book['author']}: descrizione, dettagli dell'edizione e acquisto. "
                       f"Volume Imago Artis Edizioni, {book['category'].lower()}.",
        "path": path,
    }
    jsonld = dict(ORG_JSONLD)
    schema = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": book["title"],
        "author": {"@type": "Person", "name": book["author"]},
        "publisher": {"@type": "Organization", "name": "Imago Artis Edizioni"},
        "inLanguage": "it",
        "url": SITE + path,
        "image": f"{SITE}/{book['cover']}",
        "offers": {
            "@type": "Offer",
            "price": book["price"].replace(",", "."),
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock"
            if book["availability"] == "Immediata"
            else "https://schema.org/InStoreOnly",
            "url": SITE + path,
        },
    }

    s = source
    s = re.sub(r"<title>.*?</title>\s*", "", s, flags=re.S)
    s = s.replace('<script src="https://cdn.tailwindcss.com"></script>', "")
    s = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/[^"]*" rel="stylesheet">', "", s)
    s = re.sub(r"<body\s*\n", "<body>\n", s)

    # Correzione contenuti copia-incollati
    s = re.sub(r"(<h1[^>]*>).*?(</h1>)", lambda m: m.group(1) + book["title"] + m.group(2), s, count=1, flags=re.S)
    author_label = "a cura di " + book["author"] if name == "catechismo" else "di " + book["author"]
    s = re.sub(r'(<p class="text-2xl italic text-stone-500[^>]*>).*?(</p>)',
               lambda m: m.group(1) + author_label + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r"(Prezzo di copertina</span>\s*<span[^>]*>).*?(</span>)",
               lambda m: m.group(1) + f"€ {book['price']}" + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r"(Disponibilità</span>\s*<span[^>]*>).*?(</span>)",
               lambda m: m.group(1) + book["availability"] + m.group(2), s, count=1, flags=re.S)
    s = s.replace(">Non disponibile</span>", ">Su richiesta</span>")
    s = s.replace('<span class="font-bold text-green-700">Su richiesta</span>',
                  '<span class="font-bold text-amber-700">Su richiesta</span>')

    # Immagini WebP + attributi
    s = s.replace(f'src="../{book["cover"][:-5]}.jpg"', f'src="../{book["cover"]}"')

    alt_map = {book["cover"]: f"Copertina di {book['title']} di {book['author']}"}
    s = re.sub(r"<img\b[^>]*>", lambda m: add_img_attrs(m.group(0), rel, alt_map), s)

    # Nota spedizione sotto i bottoni
    if "nota-spedizione" not in s:
        needle = "Ordina via WhatsApp</a>"
        if needle in s:
            s = s.replace(
                needle,
                needle + '\n                <p class="form-note nota-spedizione">Spedizione in tutta Italia. '
                "Con PayPal l'importo copre il libro: ti scriviamo per indirizzo e spese di spedizione.</p>",
                1,
            )

    # Navigazione + footer legale
    s = s.replace('<nav class="bg-white', '<nav aria-label="Navigazione principale" class="bg-white', 1)
    s = s.replace(
        '<a href="../contatti.html" class="hover:text-red-800">Contatti</a>',
        '<a href="../contatti.html" class="hover:text-red-800">Contatti</a>\n'
        '                    <a href="../privacy.html" class="hover:text-red-800">Privacy</a>\n'
        '                    <a href="../condizioni-di-vendita.html" class="hover:text-red-800">Condizioni di vendita</a>',
    )

    s = s.replace("</head>", seo_block(meta, rel, path, meta.get("image") or "og/" + name + ".jpg", schema) + "</head>")
    s = s.replace("<body>", '<body>\n<a class="skip-link" href="#main">Vai ai contenuti</a>')
    s = s.replace('<main class="max-w-6xl', '<main id="main" class="max-w-6xl', 1)
    return s


def transform_page(name, source):
    meta = PAGES[name]
    rel = ""
    is_book = False
    s = source
    s = re.sub(r"<title>.*?</title>\s*", "", s, flags=re.S)
    s = s.replace('<script src="https://cdn.tailwindcss.com"></script>', "")
    s = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/[^"]*" rel="stylesheet">', "", s)
    s = re.sub(r"<body\s*\n", "<body>\n", s)

    # Video hero: poster leggero e caricamento differito
    s = s.replace('target="_blank" class="bg-stone-900', 'target="_blank" rel="noopener" class="bg-stone-900')
    s = s.replace(
        '<video autoplay muted loop playsinline class="hero-video">',
        '<video autoplay muted loop playsinline preload="metadata" poster="hero-poster.webp" class="hero-video">',
    )
    s = re.sub(r"<!-- Rimosso poster.*?-->", "", s, flags=re.S)
    s = s.replace("background-image: url('04Codex.jpg')", "background-image: url('hero-poster.webp')")

    # Copertine: WebP, alt, lazy, dimensioni
    alt_map = {b["cover"]: f"Copertina di {b['title']} di {b['author']}" for b in BOOKS.values()}
    alt_map["logo.png"] = "Imago Artis Edizioni"
    s = re.sub(r"(src=)([\"'])([^\"']+)\.jpg\2", lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}.webp{m.group(2)}', s)
    s = re.sub(r"<img\b[^>]*>", lambda m: add_img_attrs(m.group(0), rel, alt_map), s)

    # Prezzi nelle card del catalogo (home e catalogo)
    s = re.sub(r'<div class="book-card">.*?</div>', card_price, s, flags=re.S)

    # Correzione Markdown rimasto nel testo
    s = s.replace("un **laboratorio di resistenza culturale**", "un <strong>laboratorio di resistenza culturale</strong>")

    # autori.html era stato copiato da una sottocartella: i link ../ non esistono in root
    s = re.sub(r'(href|src)="\.\./', r'\1="', s)
    s = s.replace('id="main" class="max-w-4xl', 'id="main" class="max-w-4xl')

    # Navigazione e footer
    s = s.replace('<nav class="bg-white', '<nav aria-label="Navigazione principale" class="bg-white', 1)
    s = s.replace(
        '<a href="contatti.html" class="hover:text-red-800">Contatti</a>',
        '<a href="contatti.html" class="hover:text-red-800">Contatti</a>\n'
        '                    <a href="privacy.html" class="hover:text-red-800">Privacy</a>\n'
        '                    <a href="condizioni-di-vendita.html" class="hover:text-red-800">Condizioni di vendita</a>',
    )

    # Form contatti funzionante
    if name == "contatti.html":
        s = re.sub(
            r'<form class="space-y-4">.*?</form>',
            """<form class="space-y-4" data-contact data-email="info@imagoartisedizioni.it" novalidate>
                <div>
                    <label class="sr-only" for="c-nome">Nome e cognome</label>
                    <input id="c-nome" name="nome" type="text" autocomplete="name" placeholder="Nome e cognome" required class="w-full p-3 bg-stone-50 border outline-none">
                </div>
                <div>
                    <label class="sr-only" for="c-email">Indirizzo email</label>
                    <input id="c-email" name="email" type="email" autocomplete="email" placeholder="Indirizzo email" required class="w-full p-3 bg-stone-50 border outline-none">
                </div>
                <div>
                    <label class="sr-only" for="c-oggetto">Motivo del contatto</label>
                    <select id="c-oggetto" name="oggetto" class="w-full p-3 bg-stone-50 border outline-none text-stone-700">
                        <option>Informazioni su un libro</option>
                        <option>Ordine e spedizione</option>
                        <option>Invio di un manoscritto</option>
                        <option>Presentazioni ed eventi</option>
                        <option>Altro</option>
                    </select>
                </div>
                <div>
                    <label class="sr-only" for="c-messaggio">Messaggio</label>
                    <textarea id="c-messaggio" name="messaggio" rows="4" placeholder="Messaggio" required class="w-full p-3 bg-stone-50 border outline-none"></textarea>
                </div>
                <label class="consent">
                    <input type="checkbox" name="privacy" required>
                    <span>Ho letto la <a href="privacy.html">informativa privacy</a> e autorizzo il trattamento dei dati per ricevere una risposta.</span>
                </label>
                <button type="submit" class="w-full bg-stone-900 text-white py-4 font-bold uppercase tracking-widest hover:bg-red-800 transition">Invia</button>
                <p class="form-status" role="status" aria-live="polite"></p>
                <p class="form-note">Si apre il tuo programma di posta con il messaggio già compilato. Preferisci WhatsApp? <a class="underline" href="https://wa.me/393286290576" target="_blank" rel="noopener">Scrivici qui</a>.</p>
            </form>""",
            s,
            count=1,
            flags=re.S,
        )

    image = meta["image"]
    s = s.replace("</head>", seo_block(meta, rel, meta["path"], image, ORG_JSONLD) + "</head>")
    s = s.replace("<body>", '<body>\n<a class="skip-link" href="#main">Vai ai contenuti</a>')
    s = re.sub(r"<main(\s)", r'<main id="main"\1', s, count=1)
    if 'id="main"' not in s:
        s = re.sub(r"<(section|header)(\s)", r'<\1 id="main"\2', s, count=1)
    return s


def main():
    if not os.path.isdir(SRC):
        raise SystemExit("Cartella sorgenti mancante: " + SRC)

    make_og()

    # Pagine principali
    for name, meta in PAGES.items():
        source = read(os.path.join(SRC, name))
        write(os.path.join(ROOT, name), transform_page(name, source))

    # Schede libro
    for name in BOOKS:
        source = read(os.path.join(SRC, name + ".html"))
        write(os.path.join(ROOT, "libri", name + ".html"), transform_book(name, source))

    # Sitemap
    urls = [("", "1.0")] + [(p["path"].lstrip("/"), "0.8") for p in PAGES.values() if p["path"] != "/"]
    urls += [(f"libri/{n}.html", "0.7") for n in BOOKS]
    urls += [("privacy.html", "0.3"), ("condizioni-di-vendita.html", "0.3")]
    entries = "\n".join(
        f"  <url><loc>{SITE}/{path}</loc><lastmod>2026-11-11</lastmod><priority>{priority}</priority></url>"
        for path, priority in urls
    )
    write(os.path.join(ROOT, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + entries + "\n</urlset>\n")

    print("Build completata: 6 pagine, %d schede libro, sitemap.xml, og/." % len(BOOKS))


if __name__ == "__main__":
    main()
