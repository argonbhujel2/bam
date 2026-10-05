# BAM Studio — Digital Experiences. Engineered.

Premium bilingual (English / नेपाली) digital agency website + full Admin CMS.

**Founder:** Argon Bhujel  
**Stack:** Flask · SQLAlchemy · PostgreSQL (Neon) · Cloudinary · Vanilla JS · Jinja2

---

## Features

### Public website
- Cinematic dark UI, large typography, scroll reveals, page loader
- Bilingual EN | नेपाली (cookie-persisted)
- Home, About, Services, Work (filterable), Project detail, Careers, Contact
- Project inquiry + contact forms
- Career application with CV upload
- SEO: meta, OG, sitemap.xml, robots.txt, Organization schema
- Responsive + `prefers-reduced-motion` support

### Admin CMS (`/admin`)
- Secure login (hashed passwords, CSRF, rate limiting, sessions)
- One-time setup at `/admin/setup` (protected by `ADMIN_SETUP_SECRET`)
- Dashboard with live counts
- Projects, categories, services, process steps
- Careers + applications (status workflow, CV download)
- Project & contact inquiries
- Media library (Cloudinary or local fallback)
- Site settings (hero, contact, social, SEO)
- Analytics (real DB counts)
- Audit logs
- Admin users (Super Admin)

### Architecture
```
ADMIN CMS → Flask + SQLAlchemy → PostgreSQL / Neon → Public site
Admin upload → Cloudinary → URL stored in DB → Public site
```

---

## Quick start

### 1. Clone & install
```bash
cd bamstudio
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, ADMIN_SETUP_SECRET
# Optional: Cloudinary, Mail
```

For local development without PostgreSQL, leave `DATABASE_URL` empty — SQLite is used automatically.

### 3. Database
```bash
export FLASK_APP=run.py
flask init-db          # creates tables + seeds sample content
# or:
flask seed             # seed only (after create_all / migrate)
```

### 4. Create first admin
1. Set `ADMIN_SETUP_SECRET` in `.env`
2. Visit `http://localhost:5000/admin/setup`
3. Create Super Admin
4. Log in at `/admin/login`
5. Remove or change `ADMIN_SETUP_SECRET` after setup

### 5. Run
```bash
python run.py
# → http://localhost:5000
# → http://localhost:5000/admin
```

---

## Production (Vercel + Neon + Cloudinary)

1. **Neon** — create PostgreSQL database, copy connection string to `DATABASE_URL` (use `postgresql://` scheme).
2. **Cloudinary** — set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.
3. **Vercel** — connect GitHub repo, set environment variables, deploy. `vercel.json` routes to `run.py`.
4. Run migrations / `flask init-db` against production DB once (e.g. from a one-off job or local with production `DATABASE_URL`).
5. Point domain via Cloudflare DNS to Vercel.

---

## Project structure

```
bamstudio/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # public, admin, admin_auth, api
│   ├── services/        # seed
│   ├── utils/           # helpers, media (Cloudinary)
│   ├── templates/
│   │   ├── public/      # site + errors
│   │   └── admin/       # CMS
│   └── static/          # css, js
├── config.py
├── run.py
├── requirements.txt
├── .env.example
├── vercel.json
└── README.md
```

---

## Content rule

No fake clients, stats, testimonials, or employees. Sample projects (Hotel Grand HMS, Pathari Sanischare Gold Cup, Jhapa FC, BAM Studio) are placeholders you can edit or replace from the admin.

---

## License

Proprietary — BAM Studio. All rights reserved.


## Ready to deploy

1. Copy `.env.example` → `.env` and set:
   - `SECRET_KEY` (long random)
   - `DATABASE_URL` (Neon PostgreSQL recommended)
   - `CLOUDINARY_*` for media
   - `MAIL_*` for notifications
   - `SITE_URL=https://your-domain.com`

2. Install & migrate:
```bash
pip install -r requirements.txt
export FLASK_APP=run.py
flask init-db
```

3. Vercel: `vercel.json` is included. Set env vars in the dashboard.
4. Cloudflare: point DNS A/CNAME to your host; enable HTTPS.
5. Production: set `FLASK_ENV=production`, `SESSION_COOKIE_SECURE=True`.

Admin: `/admin` — username `argon.bhujel` (from seed) or create via setup.
