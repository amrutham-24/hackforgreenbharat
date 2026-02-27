export interface Company {
  id: string;
  name: string;
  ticker: string | null;
  sector: string | null;
  country: string | null;
  description: string;
  logo_url: string;
}

export interface ESGScore {
  id: string;
  company_id: string;
  overall: number;
  environmental: number;
  social: number;
  governance: number;
  risk_level: "low" | "medium" | "high" | "critical";
  recorded_at: string;
}

export interface ESGEvent {
  id: string;
  company_id: string;
  title: string;
  description: string;
  source_url: string;
  category: "environmental" | "social" | "governance";
  subcategory: string;
  severity: number;
  confidence: number;
  sentiment: "positive" | "negative" | "neutral";
  event_date: string;
  created_at: string;
}

export interface Watchlist {
  id: string;
  name: string;
  created_at: string;
  items: WatchlistItem[];
}

export interface WatchlistItem {
  id: string;
  company_id: string;
  added_at: string;
}

export interface AlertRule {
  id: string;
  name: string;
  company_id: string | null;
  condition_type: string;
  threshold: number;
  category_filter: string;
  channels: string[];
  is_active: boolean;
  created_at: string;
}

export interface AlertDelivery {
  id: string;
  rule_id: string;
  event_id: string | null;
  channel: string;
  status: string;
  payload: Record<string, unknown>;
  delivered_at: string;
}

export interface Citation {
  idx: number;
  title: string;
  url: string;
  ts: string | null;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  used_company_id: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  tenant_id: string;
  email: string;
  full_name: string;
}

export interface LiveUpdate {
  type: "score_update";
  company_id: string;
  tenant_id: string;
  score: {
    overall: number;
    environmental: number;
    social: number;
    governance: number;
    risk_level: string;
  };
  event: {
    id: string;
    title: string;
    category: string;
    severity: number;
    sentiment: string;
  };
}
