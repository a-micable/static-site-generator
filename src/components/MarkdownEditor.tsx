import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { PostSummary } from "../types";

interface MarkdownEditorProps {
  posts: PostSummary[];
  onSaved?: () => void;
}

export function MarkdownEditor({ posts, onSaved }: MarkdownEditorProps) {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [markdown, setMarkdown] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePreview = useCallback(async (source: string) => {
    try {
      const { html } = await api.previewMarkdown(source);
      setPreviewHtml(html);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Preview failed");
    }
  }, []);

  useEffect(() => {
    if (posts.length > 0 && !selectedPath) {
      void handleSelectPost(posts[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [posts]);

  const handleSelectPost = async (post: PostSummary) => {
    setSelectedPath(post.path);
    setError(null);
    try {
      const detail = await api.getPost(post.path);
      setMarkdown(detail.content);
      void updatePreview(detail.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load post");
    }
  };

  const handleMarkdownChange = (value: string) => {
    setMarkdown(value);
    void updatePreview(value);
  };

  const handleSave = async () => {
    if (!selectedPath) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await api.savePost(selectedPath, markdown);
      onSaved?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save post");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="panel editor-panel" data-testid="markdown-editor">
      <header className="panel-header">
        <h2>Live Markdown Editor</h2>
        <p>Edit Markdown and preview rendered HTML instantly.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="editor-layout">
        <aside className="post-list">
          <h3>Posts</h3>
          <ul>
            {posts.map((post) => (
              <li key={post.path}>
                <button
                  type="button"
                  className={selectedPath === post.path ? "active" : ""}
                  data-testid={`post-${post.relative}`}
                  onClick={() => void handleSelectPost(post)}
                >
                  {post.title}
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="editor-pane">
          <textarea
            data-testid="markdown-input"
            value={markdown}
            onChange={(event) => handleMarkdownChange(event.target.value)}
            rows={18}
            spellCheck={false}
          />
          <div className="editor-actions">
            <button type="button" disabled={!selectedPath || saving} onClick={() => void handleSave()}>
              {saving ? "Saving…" : "Save post"}
            </button>
          </div>
        </div>

        <div
          className="preview-pane"
          data-testid="markdown-preview"
          dangerouslySetInnerHTML={{ __html: previewHtml }}
        />
      </div>
    </section>
  );
}
