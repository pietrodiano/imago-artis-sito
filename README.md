# Imago Artis Edizioni — sito

Copia di lavoro del sito `imagoartisedizioni.it`, con le correzioni tecniche applicate.
Sito statico: HTML + CSS + un piccolo JavaScript, nessun framework e nessuna build obbligatoria
(la compilazione del CSS Tailwind è opzionale ma consigliata quando modifichi le classi).

## Struttura

| Percorso | Contenuto |
| --- | --- |
| `index.html` | Home: hero video, cataloghi in evidenza, Codex, footer |
| `catalogo.html` | Catalogo completo diviso per collana |
| `territorio.html` | Progetto Memoria / ristampe storiche |
| `autori.html` | Invio manoscritti |
| `chi-siamo.html` | La redazione |
| `contatti.html` | Contatti + form |
| `libri/*.html` | 13 schede libro |
| `privacy.html` | Informativa privacy e cookie (bozza da validare) |
| `condizioni-di-vendita.html` | Condizioni di vendita, spedizioni e resi (bozza da validare) |
| `404.html` | Pagina di errore |
| `assets/site.css` | Stili condivisi (menu mobile, form, prezzi) |
| `assets/site.js` | Menu mobile e invio form |
| `assets/tailwind.css` | CSS compilato da Tailwind (sostituisce il CDN) |
| `assets/fonts.css` + `assets/fonts/` | Inter e Cormorant Garamond ospitati in locale (nessuna chiamata a Google Fonts) |
| `assets/sorgenti/` | Originali: pagine HTML di partenza, JPG e video non compressi |
| `build.py` | Rigenera le pagine dai file in `assets/sorgenti/pagine-originali/` |
| `vercel.json` | Redirect dei vecchi URL, header di sicurezza e cache |

## Modificare i contenuti

I contenuti stanno direttamente negli HTML. Se devi cambiare qualcosa che si ripete
(menu, footer, meta tag), conviene modificare `build.py` e rilanciare:

```bash
python build.py
```

Lo script legge le pagine originali da `assets/sorgenti/pagine-originali/`, applica meta tag,
menu, prezzi, immagini e correzioni, e riscrive i file in `./` e `libri/`.

## CSS

Il sito usa il CSS compilato in `assets/tailwind.css` (niente più `cdn.tailwindcss.com`).
Dopo aver aggiunto nuove classi Tailwind negli HTML:

```bash
npm install
npm run build:css
```

## Form contatti

Il form invia via `mailto:` (apre il client di posta con il messaggio già compilato) e mostra
conferma o errore. Per ricevere i messaggi direttamente senza passare dalla posta, imposta
`data-endpoint` sul form in `contatti.html`, per esempio un endpoint Formspree o una funzione
Vercel che accetta un POST JSON con `nome`, `email`, `oggetto`, `messaggio`:

```html
<form data-contact data-email="info@imagoartisedizioni.it" data-endpoint="https://...">
```

In alternativa si può collegare un servizio form-to-email e mettere l'URL in `data-endpoint`.

## Pubblicare su Vercel (da GitHub)

Il sito attuale è pubblicato su Vercel a partire dal repository **`Imagoartis/sito-imago`**
(il fork `pietrodiano/sito-imago` è fermo a giugno e contiene solo 4 file: non va usato).
Il DNS del dominio punta già a Vercel, quindi non ci sono record da cambiare: conta solo
**quale progetto Vercel** possiede il dominio.

Prima di tutto controlla nel dashboard Vercel, sotto **Settings → Domains**, se il progetto
che serve `imagoartisedizioni.it` è nel tuo account:

- **sì** → collega il nuovo repository a quel progetto (Opzione A): dominio e DNS restano intatti;
- **no** (il progetto è dell'account `Imagoartis`) → serve accesso a quell'account per spostare
  il dominio, oppure va creato un progetto nuovo e il dominio rimosso dal vecchio (Opzione B).

### 1. Creare il repository e fare il primo push

Da questa cartella:

```bash
cd imago-artis
git init -b main
git add .
git commit -m "Sito Imago Artis: correzioni tecniche, SEO, font locali"
gh repo create imago-artis-sito --private --source=. --remote=origin --push
```

Se `git commit` chiede l'identità:

```bash
git config user.name "Nome Cognome"
git config user.email "email@example.it"
```

`node_modules/` è già esclusa da `.gitignore`; `assets/sorgenti/` invece resta nel repository
ma è esclusa dal deploy da `.vercelignore`.

### 2. Collegare il repository al progetto Vercel

**Opzione A — progetto esistente (consigliata, il dominio non si sposta):**
Vercel → progetto del sito → **Settings → Git → Connect Git Repository** → scegli il nuovo
repository. Da quel momento ogni push su `main` pubblica e il dominio resta dov'è.
Se il progetto è già collegato a `Imagoartis/sito-imago`, disconnetti quel repository prima
di collegare il tuo.

**Opzione B — nuovo progetto Vercel:**
**Add New → Project → Import** il repository, framework **Other**, root directory `.`,
build command vuoto (il CSS è già compilato), output directory `.`.
Fai prima il deploy e verifica che il sito funzioni sull'URL `*.vercel.app`. Solo dopo sposta
il dominio: rimuovilo dal vecchio progetto (**Settings → Domains → Remove**) e aggiungilo al
nuovo (**Settings → Domains → Add**). Non ci sono record DNS da cambiare, ma tra la rimozione
e l'aggiunta il dominio resta irraggiungibile per qualche minuto. Se il vecchio progetto non è
nel tuo account, chiedi all'account `Imagoartis` di rimuovere il dominio o di trasferirti il progetto.

In entrambi i casi lascia vuoto il build command: `package.json` serve solo in locale per
`npm run build:css`.

### 3. Dopo il deploy verificare

- `/`, `/catalogo.html`, `/libri/rossano.html`, `/contatti.html` → 200;
- `/sitemap.xml`, `/robots.txt`, `/favicon.svg` → 200;
- un URL inesistente → pagina `404.html` personalizzata;
- `/about/`, `/services/`, `/contact/`, `/blog-2/` → redirect 301 alle pagine nuove;
- `https://www.imagoartisedizioni.it` → redirect a `https://imagoartisedizioni.it`;
- form contatti: invio, messaggio di conferma e checkbox privacy;
- immagine di anteprima incollando un link di una scheda libro in WhatsApp/Facebook.

Infine, in Google Search Console: invia `https://imagoartisedizioni.it/sitemap.xml` e controlla
che i vecchi URL risultino reindirizzati.

## Da verificare prima della pubblicazione

- **Prezzi e disponibilità**: le schede libro sono state corrette solo dove c'erano errori
  evidenti di copia-incolla. Controlla prezzo, disponibilità e autore di ogni volume.
- **Privacy e condizioni**: i testi in `privacy.html` e `condizioni-di-vendita.html` sono
  bozze complete ma vanno verificati dal titolare (sede legale, PEC, eventuale REA,
  costi di spedizione reali, tempi di consegna).
- **PayPal**: i bottoni puntano a `paypal.me/imagoartis/<importo>`, che non gestisce
  spedizione né indirizzo. Per vendite tracciabili serve un checkout con spedizione
  (PayPal Smart Buttons, Stripe o Shopify).
- **Immagini**: le copertine sono ora WebP ottimizzate; gli originali restano in
  `assets/sorgenti/` e non vengono pubblicati se non li copi nella root.
- **Font**: sono in `assets/fonts/` (solo sottoinsiemi latini). Se cambi famiglia o pesi,
  sostituisci i file e aggiorna `assets/fonts.css`.
