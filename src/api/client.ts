import type {
  BuildStatus,
  CollectionSummary,
  CreatePostPayload,
  PostDetail,
  PostSummary,
  PreviewResponse,
  SearchRecord,
  SiteConfig,
  TaxonomyMap,
} from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  getConfig: () => request<SiteConfig>("/api/config"),
  saveConfig: (config: Partial<SiteConfig>) =>
    request<SiteConfig>("/api/config", {
      method: "PUT",
      body: JSON.stringify(config),
    }),

  getPosts: (collection?: string) => {
    const query = collection ? `?collection=${encodeURIComponent(collection)}` : "";
    return request<PostSummary[]>(`/api/posts${query}`);
  },
  getPost: (path: string) =>
    request<PostDetail>(`/api/posts/${encodeURIComponent(path)}`),
  createPost: (payload: CreatePostPayload) =>
    request<PostDetail>("/api/posts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  savePost: (path: string, content: string) =>
    request<PostDetail>(`/api/posts/${encodeURIComponent(path)}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),
  deletePost: (path: string) =>
    request<void>(`/api/posts/${encodeURIComponent(path)}`, { method: "DELETE" }),
  toggleDraft: (path: string) =>
    request<PostDetail>(`/api/posts/${encodeURIComponent(path)}/draft`, {
      method: "PATCH",
    }),
  previewMarkdown: (markdown: string) =>
    request<PreviewResponse>("/api/preview", {
      method: "POST",
      body: JSON.stringify({ markdown }),
    }),

  getCollections: () => request<CollectionSummary[]>("/api/collections"),
  getTaxonomies: () => request<TaxonomyMap>("/api/taxonomies"),

  startBuild: (incremental = false, clean = false) =>
    request<BuildStatus>("/api/build", {
      method: "POST",
      body: JSON.stringify({ incremental, clean }),
    }),
  getBuildStatus: () => request<BuildStatus>("/api/build/status"),

  getSearchIndex: () => request<SearchRecord[]>("/api/search"),
};
