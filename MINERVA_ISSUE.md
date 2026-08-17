# SSG Studio — Minerva Fix Tasks

This repository contains intentional behavioral bugs for React fix-task evaluation. Each issue is user-visible and has a minimal patch.

## 1. Preview doesn't update after editing

**View:** Editor

**Steps:**
1. Open Editor and select a post.
2. Type in the Markdown pane so the preview updates.
3. Click a different post in the sidebar.

**Expected:** Preview shows the newly selected post.

**Actual:** Editor text updates but preview keeps the previous post until you type or refresh.

**Fix:** Call `updatePreview` when loading a post in `handleSelectPost` (`fix.patch`).

---

## 2. Selected tag resets after search

**View:** Tags

**Steps:**
1. Open Tags and click a tag (e.g. `python`).
2. Type in the tag search box.

**Expected:** Selected tag stays highlighted while filtering the tag list.

**Actual:** Selected tag clears whenever the search query changes.

**Fix:** Remove the `useEffect` that resets `selectedTag` on `tagSearch` change in `CollectionBrowser.tsx`.

---

## 3. Pagination loses current page

**View:** Posts

**Steps:**
1. Open Posts and go to page 2.
2. Toggle draft on any post or save a post (triggers list refresh).

**Expected:** Stay on page 2.

**Actual:** Pagination jumps back to page 1.

**Fix:** Remove or narrow the `useEffect` that resets `page` whenever `posts` changes in `PostsManager.tsx`.

---

## 4. Build status spinner never stops

**View:** Build

**Steps:**
1. Open Build and click **Build Site**.
2. Wait for the build to finish.

**Expected:** Spinner stops when `running` becomes false.

**Actual:** Spinner keeps spinning because polling is never cleared.

**Fix:** Call `stopPolling()` when `status.running` is false in `useBuild.ts`.

---

## 5. Draft toggle doesn't refresh list

**View:** Posts

**Steps:**
1. Open Posts and click **Toggle draft** on a post.

**Expected:** Draft badge updates in the list immediately.

**Actual:** List does not refresh until a manual page reload or another action triggers `onRefresh`.

**Fix:** Call `await onRefresh()` after `api.toggleDraft` in `PostsManager.tsx`.
