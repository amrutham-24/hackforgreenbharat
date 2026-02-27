import { create } from "zustand";
import type { Company, ESGScore, ESGEvent, LiveUpdate } from "@/types/api";

interface DashboardState {
  companies: Company[];
  selectedCompanyId: string | null;
  latestScores: Record<string, ESGScore>;
  scoreHistory: Record<string, ESGScore[]>;
  events: Record<string, ESGEvent[]>;
  liveUpdates: LiveUpdate[];
  sidebarOpen: boolean;
  chatOpen: boolean;

  setCompanies: (companies: Company[]) => void;
  selectCompany: (id: string) => void;
  setLatestScore: (companyId: string, score: ESGScore) => void;
  setScoreHistory: (companyId: string, scores: ESGScore[]) => void;
  setEvents: (companyId: string, events: ESGEvent[]) => void;
  addLiveUpdate: (update: LiveUpdate) => void;
  toggleSidebar: () => void;
  toggleChat: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  companies: [],
  selectedCompanyId: null,
  latestScores: {},
  scoreHistory: {},
  events: {},
  liveUpdates: [],
  sidebarOpen: true,
  chatOpen: true,

  setCompanies: (companies) => set({ companies }),

  selectCompany: (id) => set({ selectedCompanyId: id }),

  setLatestScore: (companyId, score) =>
    set((state) => ({
      latestScores: { ...state.latestScores, [companyId]: score },
    })),

  setScoreHistory: (companyId, scores) =>
    set((state) => ({
      scoreHistory: { ...state.scoreHistory, [companyId]: scores },
    })),

  setEvents: (companyId, events) =>
    set((state) => ({
      events: { ...state.events, [companyId]: events },
    })),

  addLiveUpdate: (update) =>
    set((state) => ({
      liveUpdates: [update, ...state.liveUpdates].slice(0, 50),
      latestScores: {
        ...state.latestScores,
        [update.company_id]: {
          id: "",
          company_id: update.company_id,
          ...update.score,
          recorded_at: new Date().toISOString(),
        } as ESGScore,
      },
    })),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleChat: () => set((state) => ({ chatOpen: !state.chatOpen })),
}));
