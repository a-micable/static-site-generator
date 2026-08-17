import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../src/App";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo) => {
        const url = String(input);
        if (url.startsWith("/api/posts?")) {
          return new Response(
            JSON.stringify([
              {
                path: "/site/content/posts/a.md",
                relative: "posts/a.md",
                title: "Alpha",
                collection: "posts",
                url: "posts/a/index.html",
                date: null,
                tags: [],
                categories: [],
                draft: false,
              },
            ]),
          );
        }
        if (url.startsWith("/api/config")) {
          return new Response(JSON.stringify({ title: "Site", base_url: "https://example.com" }));
        }
        if (url.startsWith("/api/collections")) {
          return new Response(JSON.stringify([]));
        }
        if (url.startsWith("/api/taxonomies")) {
          return new Response(JSON.stringify({ tags: {}, categories: {} }));
        }
        if (url.startsWith("/api/build/status")) {
          return new Response(
            JSON.stringify({
              running: false,
              pages_built: 0,
              pages_skipped: 0,
              output_dir: "",
              error: null,
              last_built_at: null,
            }),
          );
        }
        if (url.startsWith("/api/search")) {
          return new Response(JSON.stringify([]));
        }
        if (url.includes("/api/posts/")) {
          return new Response(
            JSON.stringify({
              path: "/site/content/posts/a.md",
              relative: "posts/a.md",
              title: "Alpha",
              collection: "posts",
              url: "posts/a/index.html",
              date: null,
              tags: [],
              categories: [],
              draft: false,
              content: "# Alpha\n",
            }),
          );
        }
        if (url === "/api/preview") {
          return new Response(JSON.stringify({ html: "<p>preview</p>" }));
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("renders SSG Studio navigation and editor by default", async () => {
    render(<App />);
    expect(screen.getByText("SSG Studio")).toBeInTheDocument();
    expect(await screen.findByTestId("markdown-editor")).toBeInTheDocument();
  });

  it("switches to posts manager view", async () => {
    render(<App />);
    await screen.findByTestId("markdown-editor");
    screen.getByRole("button", { name: /Posts/i }).click();
    expect(await screen.findByTestId("posts-manager")).toBeInTheDocument();
  });
});
