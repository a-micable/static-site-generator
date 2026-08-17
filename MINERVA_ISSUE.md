# Minerva Issue: Markdown preview stale on post switch

## Summary

The Markdown preview does not update when switching between posts until the page is refreshed.

## Steps to reproduce

1. Open the **Markdown Editor** view in the SSG Dashboard.
2. Select a post and type in the editor so the preview renders (the preview only updates on edit).
3. Click a different post in the sidebar.

## Expected behavior

The preview pane should immediately show HTML rendered from the newly selected post's Markdown.

## Actual behavior

The editor textarea updates to the new post content, but the preview pane continues to show the previous post's HTML until the user edits the textarea or refreshes the browser.

## Root cause

`MarkdownEditor` updates `markdown` state in `handleSelectPost` but does not call `updatePreview`. Preview refresh is only wired to `handleMarkdownChange`.

## Fix

Refresh preview when a post is selected programmatically (see `fix.patch`).
