# Minerva Submission Guide

Use this repository for a **Fix task** on the Markdown preview issue.

## Eligibility checklist

- [x] Private GitHub repository (see `Settings → General → Change visibility`)
- [x] React at repository root (`package.json`, `src/`, `vite.config.ts`)
- [x] Node 20 (`.nvmrc`, `engines` in `package.json`, CI uses Node 20)
- [x] Vitest tests via `npm test` (self-contained, mocks `fetch`)
- [x] 30+ commits with genuine project history
- [x] Original project — not a fork of a public template

## Fix task: Preview doesn't update when switching posts

**Issue:** See `MINERVA_ISSUE.md` §1

**Reproduce:**
1. Run `npm run server -- example-site` and `npm run dev`
2. Open **Editor**, select a post, type to update preview
3. Click a different post — preview stays on the previous post

**Export the fix patch** (from a tree where the bug is present):

```bash
git apply --reverse fix.patch   # introduce bug on fixed branch
git diff > fix.patch            # export fix
git apply fix.patch             # restore fixed state
npm test
```

The committed `fix.patch` replaces the stale-preview comment with `void updatePreview(detail.content)`.

## Other fix tasks

Issues §2–§5 in `MINERVA_ISSUE.md` remain intentionally unfixed for additional tasks.

## Verify before submit

```bash
nvm use
npm ci
npm test
npm run build
pytest
```
