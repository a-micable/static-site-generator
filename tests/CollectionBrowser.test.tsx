import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CollectionBrowser } from "../src/components/CollectionBrowser";

describe("CollectionBrowser", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo) => {
        const url = String(input);
        if (url === "/api/collections") {
          return new Response(
            JSON.stringify([
              {
                name: "posts",
                count: 1,
                posts: [
                  {
                    path: "/site/content/posts/a.md",
                    relative: "a.md",
                    title: "Alpha",
                    collection: "posts",
                    url: "posts/a/index.html",
                    date: null,
                    tags: ["news"],
                    categories: ["updates"],
                    draft: false,
                  },
                ],
              },
            ]),
          );
        }
        if (url === "/api/taxonomies") {
          return new Response(
            JSON.stringify({
              tags: { news: [{ title: "Alpha" }], python: [{ title: "Alpha" }] },
              categories: { updates: [{ title: "Alpha" }] },
            }),
          );
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("renders collections and tag browser", async () => {
    render(<CollectionBrowser />);
    expect(await screen.findByTestId("collection-browser")).toBeInTheDocument();
    expect(screen.getByText("Alpha")).toBeInTheDocument();
    expect(screen.getByTestId("tag-news")).toBeInTheDocument();
    expect(screen.getByText("categories")).toBeInTheDocument();
  });
});
