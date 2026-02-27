"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ChatPanel } from "@/components/chat/chat-panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { useDashboardStore } from "@/stores/dashboard";
import { api } from "@/lib/api";
import type { Watchlist, Company } from "@/types/api";
import { Star, Plus, Trash2, Building2, ArrowLeft } from "lucide-react";

export default function WatchlistClient() {
  const router = useRouter();
  const { hydrate } = useAuthStore();
  const { companies, setCompanies, latestScores } = useDashboardStore();
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    hydrate();
    const t = localStorage.getItem("esg_token");
    if (!t) {
      router.replace("/login");
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [wls, comps] = await Promise.all([
        api.getWatchlists(),
        companies.length === 0 ? api.getCompanies() : Promise.resolve(companies),
      ]);
      setWatchlists(wls);
      if (companies.length === 0) setCompanies(comps as Company[]);
    } catch {
      console.error("Failed to load watchlists");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!newName.trim()) return;
    try {
      const wl = await api.createWatchlist(newName);
      setWatchlists([...watchlists, wl]);
      setNewName("");
    } catch {
      console.error("Failed to create watchlist");
    }
  };

  const handleRemoveItem = async (watchlistId: string, companyId: string) => {
    try {
      await api.removeFromWatchlist(watchlistId, companyId);
      setWatchlists(
        watchlists.map((wl) =>
          wl.id === watchlistId
            ? { ...wl, items: wl.items.filter((i) => i.company_id !== companyId) }
            : wl
        )
      );
    } catch {
      console.error("Failed to remove item");
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-6 space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Star className="w-6 h-6 text-amber-500" />
                Watchlists
              </h1>
              <p className="text-sm text-gray-500 mt-1">Monitor your favorite companies</p>
            </div>
          </div>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Create Watchlist</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Watchlist name..."
                  className="max-w-xs"
                  onKeyDown={(e) => e.key === "Enter" && handleCreateWatchlist()}
                />
                <Button onClick={handleCreateWatchlist} disabled={!newName.trim()}>
                  <Plus className="w-4 h-4 mr-1" /> Create
                </Button>
              </div>
            </CardContent>
          </Card>

          {loading ? (
            <p className="text-sm text-gray-400">Loading watchlists...</p>
          ) : watchlists.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Star className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No watchlists yet. Create one above.</p>
              </CardContent>
            </Card>
          ) : (
            watchlists.map((wl) => (
              <Card key={wl.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Star className="w-4 h-4 text-amber-500" />
                      {wl.name}
                    </CardTitle>
                    <Badge variant="secondary">{wl.items.length} companies</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  {wl.items.length === 0 ? (
                    <p className="text-sm text-gray-400">No companies in this watchlist</p>
                  ) : (
                    <div className="space-y-2">
                      {wl.items.map((item) => {
                        const company = companies.find((c) => c.id === item.company_id);
                        const score = latestScores[item.company_id];
                        return (
                          <div
                            key={item.id}
                            className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50"
                          >
                            <button
                              onClick={() => router.push(`/company/${item.company_id}`)}
                              className="flex items-center gap-3 text-left"
                            >
                              <Building2 className="w-4 h-4 text-gray-400" />
                              <div>
                                <p className="text-sm font-medium">{company?.name || "Unknown"}</p>
                                <p className="text-xs text-gray-400">{company?.ticker} · {company?.sector}</p>
                              </div>
                            </button>
                            <div className="flex items-center gap-3">
                              {score && <span className="text-sm font-bold">{Math.round(score.overall)}</span>}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-gray-400 hover:text-red-500"
                                onClick={() => handleRemoveItem(wl.id, item.company_id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
      <ChatPanel />
    </div>
  );
}
