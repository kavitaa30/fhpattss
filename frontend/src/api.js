// Thin wrapper around the backend. Paths are relative (/api/v1/...), so the
// same code works with the Vite dev proxy and in production.
async function get(path, params = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`/api/v1/${path}${qs ? `?${qs}` : ""}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}

export const getComparison = (date, cutoff) =>
  get("comparison", { date, cutoff_hour: cutoff });
export const getMetrics = (cutoff) => get("metrics", { cutoff_hour: cutoff });
export const getByHour = (cutoff) => get("errors/by-hour", { cutoff_hour: cutoff });
export const getDistribution = (cutoff) =>
  get("errors/distribution", { cutoff_hour: cutoff });
export const getDaily = (cutoff) => get("errors/daily", { cutoff_hour: cutoff });
