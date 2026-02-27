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
import type { AlertRule, AlertDelivery } from "@/types/api";
import { Bell, Plus, ArrowLeft, Shield, Zap, Mail, MessageSquare } from "lucide-react";
import { format } from "date-fns";

export default function AlertsClient() {
  const router = useRouter();
  const { hydrate } = useAuthStore();
  const { companies, setCompanies } = useDashboardStore();
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [deliveries, setDeliveries] = useState<AlertDelivery[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState("severity_gte");
  const [formThreshold, setFormThreshold] = useState("7");

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
      const [rulesData, deliveriesData] = await Promise.all([
        api.getAlertRules(),
        api.getAlertDeliveries(),
      ]);
      setRules(rulesData);
      setDeliveries(deliveriesData);
      if (companies.length === 0) {
        const comps = await api.getCompanies();
        setCompanies(comps);
      }
    } catch {
      console.error("Failed to load alerts");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async () => {
    if (!formName.trim()) return;
    try {
      const rule = await api.createAlertRule({
        name: formName,
        condition_type: formType,
        threshold: parseFloat(formThreshold),
        channels: ["email", "slack"],
      });
      setRules([...rules, rule]);
      setFormName("");
      setShowForm(false);
    } catch {
      console.error("Failed to create rule");
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Bell className="w-6 h-6 text-amber-500" />
                  Alerts
                </h1>
                <p className="text-sm text-gray-500 mt-1">Configure and monitor ESG alert rules</p>
              </div>
            </div>
            <Button onClick={() => setShowForm(!showForm)}>
              <Plus className="w-4 h-4 mr-1" /> New Rule
            </Button>
          </div>

          {showForm && (
            <Card className="border-emerald-200 bg-emerald-50/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Create Alert Rule</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="Rule name..."
                />
                <div className="flex gap-3">
                  <select
                    value={formType}
                    onChange={(e) => setFormType(e.target.value)}
                    className="h-10 rounded-lg border border-gray-300 px-3 text-sm bg-white"
                  >
                    <option value="severity_gte">Severity &gt;=</option>
                    <option value="score_drop">Score Drop &gt;=</option>
                    <option value="category_match">Category Match</option>
                  </select>
                  <Input
                    type="number"
                    value={formThreshold}
                    onChange={(e) => setFormThreshold(e.target.value)}
                    placeholder="Threshold"
                    className="max-w-[120px]"
                  />
                  <Button onClick={handleCreateRule} disabled={!formName.trim()}>
                    Create
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="w-4 h-4" /> Active Rules
              </CardTitle>
            </CardHeader>
            <CardContent>
              {rules.length === 0 ? (
                <p className="text-sm text-gray-400 py-4 text-center">No alert rules configured</p>
              ) : (
                <div className="space-y-2">
                  {rules.map((rule) => (
                    <div key={rule.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-100">
                      <div>
                        <p className="text-sm font-medium">{rule.name}</p>
                        <p className="text-xs text-gray-400">{rule.condition_type} {">="} {rule.threshold}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {rule.channels.map((ch) => (
                          <Badge key={ch} variant="outline" className="text-xs">
                            {ch === "email" ? <Mail className="w-3 h-3 mr-1" /> : <MessageSquare className="w-3 h-3 mr-1" />}
                            {ch}
                          </Badge>
                        ))}
                        <Badge variant={rule.is_active ? "default" : "secondary"}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="w-4 h-4" /> Recent Deliveries
              </CardTitle>
            </CardHeader>
            <CardContent>
              {deliveries.length === 0 ? (
                <p className="text-sm text-gray-400 py-4 text-center">No alerts delivered yet</p>
              ) : (
                <div className="space-y-2">
                  {deliveries.map((d) => (
                    <div key={d.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-100">
                      <div>
                        <p className="text-sm font-medium">
                          {(d.payload as Record<string, string>).rule_name || "Alert"}
                        </p>
                        <p className="text-xs text-gray-400">
                          {(d.payload as Record<string, string>).message || ""}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">{d.channel}</Badge>
                        <span className="text-xs text-gray-400">
                          {format(new Date(d.delivered_at), "MMM dd HH:mm")}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
      <ChatPanel />
    </div>
  );
}
