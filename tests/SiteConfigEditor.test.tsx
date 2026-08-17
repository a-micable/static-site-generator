import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SiteConfigEditor } from "../src/components/SiteConfigEditor";

describe("SiteConfigEditor", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        if (url === "/api/config" && init?.method === "PUT") {
          const body = JSON.parse(String(init.body)) as { title: string };
          return new Response(
            JSON.stringify({
              title: body.title,
              base_url: "https://example.com",
              description: "",
              language: "en",
              author: "Author",
              feed_items: 20,
              search_index: true,
            }),
          );
        }
        if (url === "/api/config") {
          return new Response(
            JSON.stringify({
              title: "Example",
              base_url: "https://example.com",
              description: "desc",
              language: "en",
              author: "Author",
              feed_items: 20,
              search_index: true,
            }),
          );
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("loads and edits configuration", async () => {
    const user = userEvent.setup();
    render(<SiteConfigEditor />);
    expect(await screen.findByTestId("site-config-editor")).toBeInTheDocument();
    const title = screen.getByTestId("config-title");
    await user.clear(title);
    await user.type(title, "Updated Site");
    await user.click(screen.getByRole("button", { name: "Save configuration" }));
    expect(title).toHaveValue("Updated Site");
  });
});
