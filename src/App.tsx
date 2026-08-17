import { useEffect, useState } from "react";
import { api } from "./api/client";
import { BuildDashboard } from "./components/BuildDashboard";
import { CollectionBrowser } from "./components/CollectionBrowser";
import { Layout } from "./components/Layout";
import { MarkdownEditor } from "./components/MarkdownEditor";
import { PostsManager } from "./components/PostsManager";
import { SearchIndexViewer } from "./components/SearchIndexViewer";
import { SiteConfigEditor } from "./components/SiteConfigEditor";
import type { AppView, PostSummary } from "./types";
import "./App.css";

export default function App() {
  const [view, setView] = useState<AppView>("editor");
  const [posts, setPosts] = useState<PostSummary[]>([]);
  const [postsError, setPostsError] = useState<string | null>(null);

  const loadPosts = async () => {
    try {
      const data = await api.getPosts("posts");
      setPosts(data);
      setPostsError(null);
    } catch (err) {
      setPostsError(err instanceof Error ? err.message : "Failed to load posts");
    }
  };

  useEffect(() => {
    void loadPosts();
  }, []);

  return (
    <Layout activeView={view} onNavigate={setView}>
      {postsError && <p className="error banner-error">{postsError}</p>}

      {view === "editor" && (
        <MarkdownEditor posts={posts} onSaved={() => void loadPosts()} />
      )}
      {view === "posts" && (
        <PostsManager posts={posts} onRefresh={loadPosts} />
      )}
      {view === "collections" && <CollectionBrowser />}
      {view === "settings" && <SiteConfigEditor />}
      {view === "build" && <BuildDashboard />}
      {view === "search" && <SearchIndexViewer />}
    </Layout>
  );
}
