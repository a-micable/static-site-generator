import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { useConfig } from "../hooks/useConfig";
import type { SiteConfig } from "../types";

export function SiteConfigEditor() {
  const { config, loading, error, saving, save } = useConfig();
  const [form, setForm] = useState<Partial<SiteConfig>>({});

  useEffect(() => {
    if (config) {
      setForm({
        title: config.title,
        base_url: config.base_url,
        description: config.description ?? "",
        language: config.language ?? "en",
        author: config.author ?? "",
        feed_items: config.feed_items ?? 20,
        search_index: config.search_index ?? true,
      });
    }
  }, [config]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await save(form);
  };

  if (loading) {
    return <p>Loading configuration…</p>;
  }

  return (
    <section className="panel" data-testid="site-config-editor">
      <header className="panel-header">
        <h2>Site Config Editor</h2>
        <p>Edit ssg.yaml settings for your static site.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <form className="config-form" onSubmit={(event) => void handleSubmit(event)}>
        <label>
          Title
          <input
            data-testid="config-title"
            value={form.title ?? ""}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            required
          />
        </label>
        <label>
          Base URL
          <input
            data-testid="config-base-url"
            value={form.base_url ?? ""}
            onChange={(event) => setForm({ ...form, base_url: event.target.value })}
            required
          />
        </label>
        <label>
          Description
          <textarea
            value={form.description ?? ""}
            onChange={(event) => setForm({ ...form, description: event.target.value })}
            rows={3}
          />
        </label>
        <label>
          Language
          <input
            value={form.language ?? ""}
            onChange={(event) => setForm({ ...form, language: event.target.value })}
          />
        </label>
        <label>
          Author
          <input
            data-testid="config-author"
            value={form.author ?? ""}
            onChange={(event) => setForm({ ...form, author: event.target.value })}
          />
        </label>
        <label>
          Feed items
          <input
            type="number"
            min={1}
            value={form.feed_items ?? 20}
            onChange={(event) =>
              setForm({ ...form, feed_items: Number(event.target.value) })
            }
          />
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={form.search_index ?? true}
            onChange={(event) =>
              setForm({ ...form, search_index: event.target.checked })
            }
          />
          Generate search.json
        </label>
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save configuration"}
        </button>
      </form>
    </section>
  );
}
