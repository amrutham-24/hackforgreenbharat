import type {
  Company, ESGScore, ESGEvent, Watchlist, AlertRule,
  AlertDelivery, ChatResponse, LoginResponse,
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("esg_token");
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("esg_token");
      localStorage.removeItem("esg_user");
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    apiFetch<LoginResponse>("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getCompanies: (query?: string) =>
    apiFetch<Company[]>(`/v1/companies${query ? `?query=${encodeURIComponent(query)}` : ""}`),

  getCompany: (id: string) =>
    apiFetch<Company>(`/v1/companies/${id}`),

  getScores: (companyId: string, range = "30d") =>
    apiFetch<ESGScore[]>(`/v1/companies/${companyId}/scores?range=${range}`),

  getEvents: (companyId: string, range = "30d", severityGte?: number) => {
    let url = `/v1/companies/${companyId}/events?range=${range}`;
    if (severityGte) url += `&severity_gte=${severityGte}`;
    return apiFetch<ESGEvent[]>(url);
  },

  getWatchlists: () =>
    apiFetch<Watchlist[]>("/v1/watchlists"),

  getWatchlist: (id: string) =>
    apiFetch<Watchlist>(`/v1/watchlists/${id}`),

  createWatchlist: (name: string) =>
    apiFetch<Watchlist>("/v1/watchlists", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  addToWatchlist: (watchlistId: string, companyId: string) =>
    apiFetch<{ status: string; id: string }>(`/v1/watchlists/${watchlistId}/items`, {
      method: "POST",
      body: JSON.stringify({ company_id: companyId }),
    }),

  removeFromWatchlist: (watchlistId: string, companyId: string) =>
    apiFetch<{ status: string }>(`/v1/watchlists/${watchlistId}/items/${companyId}`, {
      method: "DELETE",
    }),

  getAlertRules: () =>
    apiFetch<AlertRule[]>("/v1/alerts/rules"),

  createAlertRule: (rule: {
    name: string;
    company_id?: string;
    condition_type: string;
    threshold: number;
    category_filter?: string;
    channels: string[];
  }) =>
    apiFetch<AlertRule>("/v1/alerts/rules", {
      method: "POST",
      body: JSON.stringify(rule),
    }),

  getAlertDeliveries: () =>
    apiFetch<AlertDelivery[]>("/v1/alerts/deliveries"),

  chat: (message: string, companyId?: string) =>
    apiFetch<ChatResponse>("/v1/chat", {
      method: "POST",
      body: JSON.stringify({ message, company_id: companyId }),
    }),

  ingestEvent: (event: {
    company_id: string;
    title: string;
    description: string;
    source_url?: string;
    category?: string;
  }) =>
    apiFetch<{ status: string; event_id: string }>("/v1/ingest/events", {
      method: "POST",
      body: JSON.stringify(event),
    }),
};
