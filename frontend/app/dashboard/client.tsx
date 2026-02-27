"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ChatPanel } from "@/components/chat/chat-panel";
import { ESGScorecard } from "@/components/dashboard/esg-scorecard";
import { RiskChart } from "@/components/dashboard/risk-chart";
import { EventTimeline } from "@/components/dashboard/event-timeline";
import { CompanyList } from "@/components/dashboard/company-list";
import { LiveFeed } from "@/components/dashboard/live-feed";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import { api } from "@/lib/api";
import { wsClient } from "@/lib/websocket";

export default function DashboardClient() {
  const router = useRouter();
  const { hydrate } = useAuthStore();
  const {
    companies, setCompanies, selectedCompanyId, selectCompany,
    latestScores, setLatestScore, scoreHistory, setScoreHistory,
    events, setEvents, addLiveUpdate,
  } = useDashboardStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    const t = localStorage.getItem("esg_token");
    if (!t) {
      router.replace("/login");
      return;
    }
    loadData();
  }, []);

  useEffect(() => {
    const t = localStorage.getItem("esg_token");
    if (t) {
      wsClient.connect(t);
      const unsub = wsClient.subscribe((update) => {
        addLiveUpdate(update);
      });
      return () => {
        unsub();
        wsClient.disconnect();
      };
    }
  }, [addLiveUpdate]);

  useEffect(() => {
    if (selectedCompanyId) {
      loadCompanyData(selectedCompanyId);
    }
  }, [selectedCompanyId]);

  const loadData = async () => {
    try {
      const companiesData = await api.getCompanies();
      setCompanies(companiesData);
      if (companiesData.length > 0 && !selectedCompanyId) {
        selectCompany(companiesData[0].id);
      }
    } catch {
      console.error("Failed to load companies");
    } finally {
      setLoading(false);
    }
  };

  const loadCompanyData = async (companyId: string) => {
    try {
      const [scoresData, eventsData] = await Promise.all([
        api.getScores(companyId),
        api.getEvents(companyId),
      ]);
      setScoreHistory(companyId, scoresData);
      if (scoresData.length > 0) {
        setLatestScore(companyId, scoresData[scoresData.length - 1]);
      }
      setEvents(companyId, eventsData);
    } catch {
      console.error("Failed to load company data");
    }
  };

  const currentScore = selectedCompanyId ? latestScores[selectedCompanyId] : null;
  const currentScores = selectedCompanyId ? (scoreHistory[selectedCompanyId] || []) : [];
  const currentEvents = selectedCompanyId ? (events[selectedCompanyId] || []) : [];
  const currentCompany = companies.find((c) => c.id === selectedCompanyId);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <p className="text-gray-500 text-sm">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">ESG Dashboard</h1>
              <p className="text-sm text-gray-500 mt-1">
                Real-time ESG risk intelligence for {companies.length} companies
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
              </span>
              <span className="text-xs text-gray-500">Live</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <ESGScorecard score={currentScore || null} companyName={currentCompany?.name} />
              <LiveFeed />
            </div>
            <div className="lg:col-span-2 space-y-6">
              <RiskChart scores={currentScores} />
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <EventTimeline events={currentEvents} />
                <CompanyList />
              </div>
            </div>
          </div>
        </div>
      </main>
      <ChatPanel />
    </div>
  );
}
