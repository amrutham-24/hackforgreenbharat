"use client";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useDashboardStore } from "@/stores/dashboard";
import { useRouter } from "next/navigation";
import { Building2, Search, TrendingDown, TrendingUp, Minus } from "lucide-react";

export function CompanyList() {
  const router = useRouter();
  const { companies, latestScores, selectCompany } = useDashboardStore();
  const [search, setSearch] = useState("");

  const filtered = companies.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.ticker && c.ticker.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Companies</CardTitle>
        <div className="relative mt-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search companies..."
            className="pl-9 text-xs h-9"
          />
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-72">
          <div className="space-y-1">
            {filtered.map((company) => {
              const score = latestScores[company.id];
              return (
                <button
                  key={company.id}
                  onClick={() => {
                    selectCompany(company.id);
                    router.push(`/company/${company.id}`);
                  }}
                  className="flex items-center justify-between w-full p-2.5 rounded-lg hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-4 h-4 text-gray-500" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{company.name}</p>
                      <p className="text-[10px] text-gray-400">{company.ticker} · {company.sector}</p>
                    </div>
                  </div>
                  {score && (
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-sm font-bold text-gray-900">{Math.round(score.overall)}</span>
                      <Badge
                        variant={
                          score.risk_level === "low" ? "default" :
                          score.risk_level === "medium" ? "warning" : "destructive"
                        }
                        className="text-[10px]"
                      >
                        {score.risk_level}
                      </Badge>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
