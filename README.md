# SSG Studio

SSG Studio is a React + TypeScript frontend for the Python Static Site Generator. It provides live editing, preview, content management, and build monitoring while using the existing Python engine.

## Features

- **Live Markdown Editor** — split-pane editor with instant HTML preview
- **Posts Manager** — create, edit, delete, and paginate posts
- **Tags & Categories** — browse taxonomies and filter tagged content
- **Site Settings** — edit `ssg.yaml` configuration
- **Build Dashboard** — run builds with live status
- **Search** — filter content from `search.json`

## Quick Start

```bash
npm install
pip install -e ".[dev]"

# Terminal 1 — Python API
npm run server -- example-site

# Terminal 2 — React app
npm run dev
```

Open http://127.0.0.1:5173/

## Testing

```bash
npm test          # Vitest — React components
npm run build     # Production build
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

See `MINERVA_ISSUE.md` for five intentional behavioral bugs. Apply the sample preview fix:

```bash
git apply fix.patch
```

## Python Engine

The Python CLI remains available:

```bash
ssg build example-site
ssg serve example-site
ssg init my-site
```

## License

MIT
