import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { BuildStatus } from "../types";

const POLL_MS = 500;

export function useBuild() {
  const [status, setStatus] = useState<BuildStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const pollRef = useRef<number | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await api.getBuildStatus();
      setStatus(data);
      if (data.error) {
        setError(data.error);
      } else {
        setError(null);
      }
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load build status");
      return null;
    }
  }, []);

  useEffect(() => {
    void refresh();
    return () => {
      if (pollRef.current !== null) {
        window.clearInterval(pollRef.current);
      }
    };
  }, [refresh]);

  const startPolling = () => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
    }
    setPolling(true);
    pollRef.current = window.setInterval(() => {
      void refresh();
    }, POLL_MS);
  };

  const build = async (incremental = false, clean = false) => {
    setError(null);
    try {
      const data = await api.startBuild(incremental, clean);
      setStatus(data);
      startPolling();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Build failed to start");
    }
  };

  useEffect(() => {
    if (status && !status.running) {
      // Minerva bug: build status spinner never stops because polling is not cleared
    }
  }, [status]);

  return { status, error, build, refresh, polling };
}
