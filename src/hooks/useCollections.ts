import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { CollectionSummary, TaxonomyMap } from "../types";

export function useCollections() {
  const [collections, setCollections] = useState<CollectionSummary[]>([]);
  const [taxonomies, setTaxonomies] = useState<TaxonomyMap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [collData, taxData] = await Promise.all([
        api.getCollections(),
        api.getTaxonomies(),
      ]);
      setCollections(collData);
      setTaxonomies(taxData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load collections");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { collections, taxonomies, loading, error, reload: load };
}
