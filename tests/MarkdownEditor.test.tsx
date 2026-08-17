import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MarkdownEditor } from "../src/components/MarkdownEditor";

const posts = [
  {
    path: "/site/content/posts/first.md",
    relative: "posts/first.md",
    title: "First",
    collection: "posts",
    url: "posts/first/index.html",
    date: null,
    tags: [],
    categories: [],
    draft: false,
  },
  {
    path: "/site/content/posts/second.md",
    relative: "posts/second.md",
    title: "Second",
    collection: "posts",
    url: "posts/second/index.html",
    date: null,
    tags: [],
    categories: [],
    draft: false,
  },
];

describe("MarkdownEditor", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        if (url.includes("first.md")) {
          return new Response(JSON.stringify({ ...posts[0], content: "# First content" }));
        }
        if (url.includes("second.md")) {
          return new Response(JSON.stringify({ ...posts[1], content: "# Second content" }));
        }
        if (url === "/api/preview") {
          const body = JSON.parse(String(init?.body ?? "{}")) as { markdown: string };
          return new Response(
            JSON.stringify({
              html: body.markdown.includes("Second")
                ? "<h1>Second content</h1>"
                : "<h1>First content</h1>",
            }),
          );
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("renders editor and loads first post", async () => {
    render(<MarkdownEditor posts={posts} />);
    expect(await screen.findByTestId("markdown-editor")).toBeInTheDocument();
    expect(screen.getByTestId("markdown-input")).toHaveValue("# First content");
  });

  it.skip("Minerva fix: updates preview when switching posts", async () => {
    const user = userEvent.setup();
    render(<MarkdownEditor posts={posts} />);
    await screen.findByTestId("markdown-input");
    await user.click(screen.getByTestId("post-posts/second.md"));
    expect(screen.getByTestId("markdown-input")).toHaveValue("# Second content");
    expect(await screen.findByTestId("markdown-preview")).toContainHTML(
      "<h1>Second content</h1>",
    );
  });
});
