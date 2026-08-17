import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { SiteConfig } from "../types";

export function useConfig() {
  const [config, setConfig] = useState<SiteConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getConfig();
      setConfig(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load config");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const save = async (partial: Partial<SiteConfig>) => {
    setSaving(true);
    try {
      const data = await api.saveConfig(partial);
      setConfig(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save config");
      throw err;
    } finally {
      setSaving(false);
    }
  };

  return { config, loading, saving, error, reload: load, save };
}
