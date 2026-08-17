import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { PostSummary } from "../types";

const PAGE_SIZE = 5;

interface PostsManagerProps {
  posts: PostSummary[];
  onRefresh: () => Promise<void>;
}

export function PostsManager({ posts, onRefresh }: PostsManagerProps) {
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState("");
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [error, setError] = useState<string | null>(null);

  const filtered = posts.filter((post) => {
    const needle = filter.trim().toLowerCase();
    if (!needle) return true;
    return (
      post.title.toLowerCase().includes(needle) ||
      post.tags.some((tag) => tag.toLowerCase().includes(needle))
    );
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pagePosts = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // Minerva bug: pagination loses current page whenever posts list updates
  useEffect(() => {
    setPage(1);
  }, [posts]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const loadPost = useCallback(async (path: string) => {
    setSelectedPath(path);
    setError(null);
    try {
      const detail = await api.getPost(path);
      setContent(detail.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load post");
    }
  }, []);

  useEffect(() => {
    if (pagePosts.length > 0 && !selectedPath) {
      void loadPost(pagePosts[0].path);
    }
  }, [pagePosts, selectedPath, loadPost]);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const created = await api.createPost({ title: newTitle.trim(), collection: "posts" });
      setNewTitle("");
      await onRefresh();
      await loadPost(created.path);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create post");
    } finally {
      setCreating(false);
    }
  };

  const handleSave = async () => {
    if (!selectedPath) return;
    setSaving(true);
    setError(null);
    try {
      await api.savePost(selectedPath, content);
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save post");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedPath || !window.confirm("Delete this post?")) return;
    setError(null);
    try {
      await api.deletePost(selectedPath);
      setSelectedPath(null);
      setContent("");
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete post");
    }
  };

  const handleDraftToggle = async (post: PostSummary) => {
    setError(null);
    try {
      await api.toggleDraft(post.path);
      // Minerva bug: draft toggle does not refresh the posts list
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle draft");
    }
  };

  return (
    <section className="panel" data-testid="posts-manager">
      <header className="panel-header row-header">
        <div>
          <h2>Posts Manager</h2>
          <p>Create, edit, and delete Markdown posts.</p>
        </div>
        <div className="header-actions">
          <input
            data-testid="posts-filter"
            placeholder="Filter posts…"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
          <input
            data-testid="new-post-title"
            placeholder="New post title"
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
          />
          <button type="button" data-testid="create-post" disabled={creating} onClick={() => void handleCreate()}>
            {creating ? "Creating…" : "New Post"}
          </button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="posts-layout">
        <aside className="post-list">
          <ul data-testid="posts-list">
            {pagePosts.map((post) => (
              <li key={post.path}>
                <button
                  type="button"
                  className={selectedPath === post.path ? "active" : ""}
                  data-testid={`manage-post-${post.relative}`}
                  onClick={() => void loadPost(post.path)}
                >
                  {post.title}
                  {post.draft && <span className="badge draft">Draft</span>}
                </button>
                <button
                  type="button"
                  className="ghost-btn"
                  data-testid={`draft-toggle-${post.relative}`}
                  onClick={() => void handleDraftToggle(post)}
                >
                  Toggle draft
                </button>
              </li>
            ))}
          </ul>

          <nav className="pagination" data-testid="posts-pagination">
            <button type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <span data-testid="posts-page-indicator">
              Page {page} of {totalPages}
            </span>
            <button type="button" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Next
            </button>
          </nav>
        </aside>

        <div className="editor-pane">
          <textarea
            data-testid="post-content-input"
            value={content}
            onChange={(event) => setContent(event.target.value)}
            rows={20}
            spellCheck={false}
          />
          <div className="editor-actions">
            <button type="button" disabled={!selectedPath || saving} onClick={() => void handleSave()}>
              {saving ? "Saving…" : "Save Changes"}
            </button>
            <button type="button" className="danger-btn" disabled={!selectedPath} onClick={() => void handleDelete()}>
              Delete
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
