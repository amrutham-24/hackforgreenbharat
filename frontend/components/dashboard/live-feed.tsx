"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useDashboardStore } from "@/stores/dashboard";
import { Zap, TrendingDown, TrendingUp } from "lucide-react";

export function LiveFeed() {
  const { liveUpdates, companies } = useDashboardStore();

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500" />
          <CardTitle className="text-base">Live Updates</CardTitle>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-48">
          {liveUpdates.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-6">
              Listening for real-time updates...
            </p>
          ) : (
            <div className="space-y-2">
              {liveUpdates.map((update, i) => {
                const company = companies.find((c) => c.id === update.company_id);
                return (
                  <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
                    <div className="flex-shrink-0 mt-1">
                      {update.score.overall >= 70 ? (
                        <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <TrendingDown className="w-3.5 h-3.5 text-red-500" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-gray-900">
                        {company?.name || "Company"}: Score {Math.round(update.score.overall)}
                      </p>
                      <p className="text-[10px] text-gray-500 truncate mt-0.5">
                        {update.event.title}
                      </p>
                      <div className="flex gap-1 mt-1">
                        <Badge variant="outline" className="text-[9px]">
                          {update.event.category}
                        </Badge>
                        <Badge
                          variant={update.event.severity >= 7 ? "destructive" : "secondary"}
                          className="text-[9px]"
                        >
                          Sev: {update.event.severity}
                        </Badge>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
