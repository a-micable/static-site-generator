import { useEffect, useMemo, useState } from "react";
import { useCollections } from "../hooks/useCollections";

export function CollectionBrowser() {
  const { collections, taxonomies, loading, error } = useCollections();
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [tagSearch, setTagSearch] = useState("");

  const tagNames = useMemo(
    () => Object.keys(taxonomies?.tags ?? {}).sort(),
    [taxonomies],
  );

  const filteredTags = tagNames.filter((tag) =>
    tag.toLowerCase().includes(tagSearch.trim().toLowerCase()),
  );

  // Minerva bug: selected tag resets whenever the search query changes
  useEffect(() => {
    setSelectedTag(null);
  }, [tagSearch]);

  const selectedPosts = selectedTag ? taxonomies?.tags[selectedTag] ?? [] : [];

  if (loading) {
    return <p>Loading collections…</p>;
  }

  return (
    <section className="panel" data-testid="collection-browser">
      <header className="panel-header">
        <h2>Tags &amp; Categories</h2>
        <p>Browse collections, filter tags, and inspect categorized content.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <div className="collection-grid">
        {collections.map((collection) => (
          <article key={collection.name} className="card">
            <h3>{collection.name}</h3>
            <p>{collection.count} posts</p>
            <ul>
              {collection.posts.slice(0, 5).map((post) => (
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

      <div className="taxonomy-browser">
        <div className="taxonomy-sidebar">
          <label className="search-filter-label">
            Search tags
            <input
              data-testid="tag-search"
              value={tagSearch}
              onChange={(event) => setTagSearch(event.target.value)}
              placeholder="Filter tags…"
            />
          </label>
          <ul className="tag-list" data-testid="tag-list">
            {filteredTags.map((tag) => (
              <li key={tag}>
                <button
                  type="button"
                  className={selectedTag === tag ? "active" : ""}
                  data-testid={`tag-${tag}`}
                  onClick={() => setSelectedTag(tag)}
                >
                  {tag}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="taxonomy-detail" data-testid="tag-detail">
          {selectedTag ? (
            <>
              <h3 data-testid="selected-tag">{selectedTag}</h3>
              <ul>
                {selectedPosts.map((post) => (
                  <li key={post.path}>{post.title}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="muted">Select a tag to view posts.</p>
          )}
        </div>
      </div>

      {taxonomies && (
        <div className="taxonomy-grid">
          <article className="card">
            <h3>categories</h3>
            <ul>
              {Object.entries(taxonomies.categories).map(([name, items]) => (
                <li key={name}>
                  <strong>{name}</strong> ({items.length})
                </li>
              ))}
            </ul>
          </article>
        </div>
      )}
    </section>
  );
}
