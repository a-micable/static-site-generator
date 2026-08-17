import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SearchIndexViewer } from "../src/components/SearchIndexViewer";

const records = [
  {
    title: "Alpha Post",
    url: "https://example.com/posts/alpha/index.html",
    path: "posts/alpha/index.html",
    collection: "posts",
    date: "2024-01-01",
    tags: ["news"],
    categories: [],
    taxonomies: { tags: ["news"] },
    summary: "",
    content: "alpha content about python",
  },
  {
    title: "Beta Post",
    url: "https://example.com/posts/beta/index.html",
    path: "posts/beta/index.html",
    collection: "posts",
    date: "2024-02-01",
    tags: ["updates"],
    categories: [],
    taxonomies: { tags: ["updates"] },
    summary: "",
    content: "beta content about ssg",
  },
];

describe("SearchIndexViewer", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo) => {
        if (String(input) === "/api/search") {
          return new Response(JSON.stringify(records));
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("renders search records", async () => {
    render(<SearchIndexViewer />);
    expect(await screen.findByTestId("search-index-viewer")).toBeInTheDocument();
    expect(screen.getByText("Alpha Post")).toBeInTheDocument();
    expect(screen.getByTestId("search-count")).toHaveTextContent("2 records");
  });

  it("filters records by query", async () => {
    const user = userEvent.setup();
    render(<SearchIndexViewer />);
    await screen.findByTestId("search-index-viewer");
    await user.type(screen.getByTestId("search-filter"), "beta");
    expect(screen.getByTestId("search-count")).toHaveTextContent("1 records");
    expect(screen.getByText("Beta Post")).toBeInTheDocument();
  });
});
