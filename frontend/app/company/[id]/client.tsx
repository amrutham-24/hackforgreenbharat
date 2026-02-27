"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ChatPanel } from "@/components/chat/chat-panel";
import { ESGScorecard } from "@/components/dashboard/esg-scorecard";
import { RiskChart } from "@/components/dashboard/risk-chart";
import { EventTimeline } from "@/components/dashboard/event-timeline";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import { api } from "@/lib/api";
import type { Company, ESGScore, ESGEvent } from "@/types/api";
import { ArrowLeft, Building2, Globe, MapPin } from "lucide-react";

export default function CompanyClient() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;
  const { hydrate } = useAuthStore();
  const { selectCompany, setCompanies, companies } = useDashboardStore();
  const [company, setCompany] = useState<Company | null>(null);
  const [scores, setScores] = useState<ESGScore[]>([]);
  const [events, setEvents] = useState<ESGEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    hydrate();
    const t = localStorage.getItem("esg_token");
    if (!t) {
      router.replace("/login");
      return;
    }
    selectCompany(companyId);
    loadData();
  }, [companyId]);

  const loadData = async () => {
    try {
      const [companyData, scoresData, eventsData] = await Promise.all([
        api.getCompany(companyId),
        api.getScores(companyId, "60d"),
        api.getEvents(companyId, "60d"),
      ]);
      setCompany(companyData);
      setScores(scoresData);
      setEvents(eventsData);
      if (companies.length === 0) {
        const allCompanies = await api.getCompanies();
        setCompanies(allCompanies);
      }
    } catch {
      console.error("Failed to load company");
    } finally {
      setLoading(false);
    }
  };

  const latestScore = scores.length > 0 ? scores[scores.length - 1] : null;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading company data...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-6 space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-gray-500" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{company?.name}</h1>
                <div className="flex items-center gap-3 mt-0.5">
                  {company?.ticker && <Badge variant="outline" className="text-xs">{company.ticker}</Badge>}
                  {company?.sector && (
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Globe className="w-3 h-3" /> {company.sector}
                    </span>
                  )}
                  {company?.country && (
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> {company.country}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {company?.description && (
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-gray-600">{company.description}</p>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <ESGScorecard score={latestScore} companyName={company?.name} />
            <div className="lg:col-span-2">
              <RiskChart scores={scores} />
            </div>
          </div>

          <EventTimeline events={events} />
        </div>
      </main>
      <ChatPanel />
    </div>
  );
}
