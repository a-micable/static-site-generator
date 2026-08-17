import { useSearchIndex } from "../hooks/useSearchIndex";

export function SearchIndexViewer() {
  const { filtered, loading, error, query, setQuery } = useSearchIndex();

  if (loading) {
    return <p>Loading search index…</p>;
  }

  return (
    <section className="panel" data-testid="search-index-viewer">
      <header className="panel-header">
        <h2>Search Content</h2>
        <p>Search across titles, tags, and rendered content from search.json.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <label className="search-filter-label">
        Search
        <input
          data-testid="search-filter"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search titles, tags, content…"
        />
      </label>

      <p data-testid="search-count">{filtered.length} records</p>

      <ul className="search-results">
        {filtered.map((record) => (
          <li key={record.path} className="search-record">
            <strong>{record.title}</strong>
            <span className="meta">{record.path}</span>
            {record.tags.length > 0 && (
              <span className="meta">tags: {record.tags.join(", ")}</span>
            )}
            <p className="snippet">{record.content.slice(0, 140)}…</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
