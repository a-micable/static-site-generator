import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PostsManager } from "../src/components/PostsManager";

const posts = Array.from({ length: 6 }, (_, index) => ({
  path: `/site/content/posts/post-${index + 1}.md`,
  relative: `posts/post-${index + 1}.md`,
  title: `Post ${index + 1}`,
  collection: "posts",
  url: `posts/post-${index + 1}/index.html`,
  date: null,
  tags: [],
  categories: [],
  draft: false,
}));

describe("PostsManager", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        if (url.includes("/api/posts/") && init?.method === "PUT") {
          return new Response(JSON.stringify({ ...posts[0], content: "saved" }));
        }
        if (url.includes("/api/posts/")) {
          return new Response(JSON.stringify({ ...posts[0], content: "# Content" }));
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("paginates posts", async () => {
    const user = userEvent.setup();
    render(<PostsManager posts={posts} onRefresh={async () => undefined} />);
    expect(await screen.findByTestId("posts-page-indicator")).toHaveTextContent("Page 1 of 2");
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByTestId("posts-page-indicator")).toHaveTextContent("Page 2 of 2");
  });
});
