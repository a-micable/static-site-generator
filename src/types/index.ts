export type AppView = "editor" | "posts" | "collections" | "settings" | "build" | "search";

export interface SiteConfig {
  title: string;
  base_url: string;
  description?: string;
  language?: string;
  author?: string;
  feed_items?: number;
  search_index?: boolean;
  output_dir?: string;
  content_dir?: string;
  templates_dir?: string;
  assets_dir?: string;
}

export interface PostSummary {
  path: string;
  relative: string;
  title: string;
  collection: string | null;
  url: string;
  date: string | null;
  tags: string[];
  categories: string[];
  draft: boolean;
}

export interface PostDetail extends PostSummary {
  content: string;
}

export interface CollectionSummary {
  name: string;
  count: number;
  posts: PostSummary[];
}

export interface TaxonomyMap {
  tags: Record<string, PostSummary[]>;
  categories: Record<string, PostSummary[]>;
}

export interface BuildStatus {
  running: boolean;
  pages_built: number;
  pages_skipped: number;
  output_dir: string;
  error: string | null;
  last_built_at: string | null;
}

export interface SearchRecord {
  title: string;
  url: string;
  path: string;
  collection: string | null;
  date: string | null;
  tags: string[];
  categories: string[];
  taxonomies: Record<string, string[]>;
  summary: string;
  content: string;
}

export interface PreviewResponse {
  html: string;
}

export interface CreatePostPayload {
  title: string;
  collection?: string;
  slug?: string;
}
