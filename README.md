# SSG Studio

SSG Studio is a React + TypeScript frontend for the Python Static Site Generator. It provides live editing, preview, content management, and build monitoring while using the existing Python engine.

## Features

- **Live Markdown Editor** — split-pane editor with instant HTML preview
- **Posts Manager** — create, edit, delete, paginate, and toggle drafts
- **Tags & Categories** — browse taxonomies and filter tagged content
- **Site Settings** — edit `ssg.yaml` configuration
- **Build Dashboard** — run builds with live status
- **Search** — filter content from `search.json`

## Requirements

- Node.js 20+
- Python 3.11+ (for the SSG engine and API server)

## Quick Start

```bash
nvm use          # Node 20 — see .nvmrc
npm ci
pip install -e ".[dev]"

# Terminal 1 — Python API
npm run server -- example-site

# Terminal 2 — React app
npm run dev
```

Open http://127.0.0.1:5173/

## Testing

```bash
npm test          # Vitest — React components (no live API required)
npm run build     # Typecheck + production build
pytest            # Python engine + API
```

## Project Structure

```
static-site-generator/
├── src/                 # React application (SSG Studio)
│   ├── components/      # UI views and forms
│   ├── hooks/           # State and data fetching
│   └── api/             # JSON API client
├── ssg/                 # Python static site generator engine
├── tests/               # Vitest + pytest suites
├── package.json
├── vite.config.ts
└── README.md
```

## Minerva Fix Tasks

This repository includes intentional behavioral bugs for React fix-task evaluation. See:

- `MINERVA_ISSUE.md` — issue descriptions
- `MINERVA_SUBMISSION.md` — submission checklist
- `fix.patch` — minimal fix for the preview-on-post-switch issue

## Python CLI

The Python engine remains available:

```bash
ssg build example-site
ssg serve example-site
ssg init my-site
```

## License

MIT
