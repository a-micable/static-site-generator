import { useCollections } from "../hooks/useCollections";

export function CollectionBrowser() {
  const { collections, taxonomies, loading, error } = useCollections();

  if (loading) {
    return <p>Loading collections…</p>;
  }

  return (
    <section className="panel" data-testid="collection-browser">
      <header className="panel-header">
        <h2>Collection Browser</h2>
        <p>Browse posts, tags, and categories across collections.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="collection-grid">
        {collections.map((collection) => (
          <article key={collection.name} className="card">
            <h3>{collection.name}</h3>
            <p>{collection.count} posts</p>
            <ul>
              {collection.posts.map((post) => (
                <li key={post.path}>
                  <strong>{post.title}</strong>
                  {post.tags.length > 0 && (
                    <span className="meta"> — {post.tags.join(", ")}</span>
                  )}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      {taxonomies && (
        <div className="taxonomy-grid">
          {(["tags", "categories"] as const).map((kind) => (
            <article key={kind} className="card">
              <h3>{kind}</h3>
              <ul>
                {Object.entries(taxonomies[kind]).map(([name, items]) => (
                  <li key={name}>
                    <strong>{name}</strong> ({items.length})
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
