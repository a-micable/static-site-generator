import { useBuild } from "../hooks/useBuild";

export function BuildDashboard() {
  const { status, error, build, refresh } = useBuild();

  return (
    <section className="panel" data-testid="build-dashboard">
      <header className="panel-header">
        <h2>Build Dashboard</h2>
        <p>Run builds and monitor generated output.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="build-actions">
        <button type="button" data-testid="build-full" disabled={status?.running} onClick={() => void build(false, false)}>
          Full build
        </button>
        <button
          type="button"
          data-testid="build-incremental"
          disabled={status?.running}
          onClick={() => void build(true, false)}
        >
          Incremental build
        </button>
        <button type="button" data-testid="build-clean" disabled={status?.running} onClick={() => void build(false, true)}>
          Clean build
        </button>
        <button type="button" onClick={() => void refresh()}>
          Refresh status
        </button>
      </div>

      <dl className="build-status" data-testid="build-status">
        <div>
          <dt>Running</dt>
          <dd data-testid="build-running">{status?.running ? "yes" : "no"}</dd>
        </div>
        <div>
          <dt>Pages built</dt>
          <dd data-testid="build-pages-built">{status?.pages_built ?? 0}</dd>
        </div>
        <div>
          <dt>Pages skipped</dt>
          <dd>{status?.pages_skipped ?? 0}</dd>
        </div>
        <div>
          <dt>Output directory</dt>
          <dd>{status?.output_dir || "—"}</dd>
        </div>
        <div>
          <dt>Last built</dt>
          <dd>{status?.last_built_at ?? "—"}</dd>
        </div>
      </dl>
    </section>
  );
}
