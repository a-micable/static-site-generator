import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { SearchRecord } from "../types";

export function useSearchIndex() {
  const [records, setRecords] = useState<SearchRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getSearchIndex();
      setRecords(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load search index");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) {
      return records;
    }
    return records.filter((record) => {
      const haystack = [
        record.title,
        record.content,
        record.path,
        record.collection ?? "",
        ...record.tags,
        ...record.categories,
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(needle);
    });
  }, [query, records]);

  return { records, filtered, loading, error, query, setQuery, reload: load };
}
