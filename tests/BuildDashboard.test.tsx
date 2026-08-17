import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BuildDashboard } from "../src/components/BuildDashboard";

describe("BuildDashboard", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        if (url === "/api/build/status") {
          return new Response(
            JSON.stringify({
              running: false,
              pages_built: 5,
              pages_skipped: 2,
              output_dir: "/site/dist",
              error: null,
              last_built_at: "2024-01-01T00:00:00+00:00",
            }),
          );
        }
        if (url === "/api/build" && init?.method === "POST") {
          return new Response(
            JSON.stringify({
              running: true,
              pages_built: 0,
              pages_skipped: 0,
              output_dir: "/site/dist",
              error: null,
              last_built_at: null,
            }),
          );
        }
        return new Response("not found", { status: 404 });
      }),
    );
  });

  it("renders build status", async () => {
    render(<BuildDashboard />);
    expect(await screen.findByTestId("build-dashboard")).toBeInTheDocument();
    expect(screen.getByTestId("build-pages-built")).toHaveTextContent("5");
  });

  it("starts a build", async () => {
    const user = userEvent.setup();
    render(<BuildDashboard />);
    await screen.findByTestId("build-dashboard");
    await user.click(screen.getByTestId("build-full"));
    expect(await screen.findByTestId("build-running")).toHaveTextContent("yes");
  });
});
