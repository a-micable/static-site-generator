# Minerva Fix Tasks

Intentional user-visible bugs for React fix-task evaluation. Each has a minimal, focused fix.

## 1. Preview doesn't update when switching posts ✅ `fix.patch`

**View:** Editor

**Steps:**
1. Open Editor and select a post.
2. Type in the Markdown pane so the preview updates.
3. Click a different post in the sidebar.

**Expected:** Preview shows the newly selected post immediately.

**Actual:** Editor text updates but preview keeps the previous HTML until you type or refresh.

**Fix:** In `MarkdownEditor.tsx`, call `void updatePreview(detail.content)` after loading a post in `handleSelectPost`.

---

## 2. Selected tag resets after search

**View:** Tags

**Steps:**
1. Open Tags and select a tag.
2. Type in the tag search box.

**Expected:** Selected tag stays highlighted while filtering the list.

**Actual:** Selection clears on every search keystroke.

**Fix:** Remove the `useEffect` that sets `selectedTag` to `null` when `tagSearch` changes in `CollectionBrowser.tsx`.

---

## 3. Pagination loses current page

**View:** Posts

**Steps:**
1. Open Posts and navigate to page 2.
2. Save a post or toggle draft (triggers list refresh).

**Expected:** Remain on page 2.

**Actual:** Pagination jumps back to page 1.

**Fix:** Remove or narrow the `useEffect` that resets `page` whenever `posts` changes in `PostsManager.tsx`.

---

## 4. Build status spinner never stops

**View:** Build

**Steps:**
1. Click **Build Site**.
2. Wait for the build to finish.

**Expected:** Spinner stops when `running` becomes false.

**Actual:** Spinner keeps spinning because polling is never cleared.

**Fix:** Clear the polling interval when `status.running` is false in `useBuild.ts`.

---

## 5. Draft toggle doesn't refresh list

**View:** Posts

**Steps:**
1. Click **Toggle draft** on a post.

**Expected:** Draft badge updates immediately in the list.

**Actual:** List does not refresh until manual reload.

**Fix:** Call `await onRefresh()` after `api.toggleDraft` in `PostsManager.tsx`.
