import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { PostSummary } from "../types";

interface MarkdownEditorProps {
  posts: PostSummary[];
  onSaved?: () => void;
}

export function MarkdownEditor({ posts, onSaved }: MarkdownEditorProps) {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [filename, setFilename] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
  const [previewVisible, setPreviewVisible] = useState(true);
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
    setFilename(post.relative);
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
    if (!selectedPath) return;
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

  const handleDelete = async () => {
    if (!selectedPath || !window.confirm("Delete this post?")) return;
    try {
      await api.deletePost(selectedPath);
      setSelectedPath(null);
      setMarkdown("");
      setPreviewHtml("");
      onSaved?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete post");
    }
  };

  return (
    <section className="studio-editor" data-testid="markdown-editor">
      <header className="editor-toolbar">
        <div className="toolbar-left">
          <span className="toolbar-label">MARKDOWN</span>
          <span className="file-chip" data-testid="active-filename">
            {filename || "no file selected"}
          </span>
        </div>
        <div className="toolbar-right">
          <button type="button" className="icon-btn danger-btn" disabled={!selectedPath} onClick={() => void handleDelete()}>
            Delete
          </button>
          <button type="button" className="primary-btn" disabled={!selectedPath || saving} onClick={() => void handleSave()}>
            {saving ? "Saving…" : "Save Changes"}
          </button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="studio-editor-body">
        <aside className="post-list compact">
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

        <div className="split-editor">
          <div className="editor-pane labeled-pane">
            <div className="pane-label">MARKDOWN</div>
            <textarea
              data-testid="markdown-input"
              aria-label="Markdown source"
              value={markdown}
              onChange={(event) => handleMarkdownChange(event.target.value)}
              spellCheck={false}
            />
          </div>

          <div className="preview-pane labeled-pane">
            <div className="pane-label">
              PREVIEW
              <button
                type="button"
                className="ghost-btn"
                data-testid="toggle-preview"
                onClick={() => setPreviewVisible((visible) => !visible)}
              >
                {previewVisible ? "Hide" : "Show"}
              </button>
            </div>
            {previewVisible && (
              <div
                className="preview-content"
                data-testid="markdown-preview"
                role="region"
                aria-label="Markdown preview"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
