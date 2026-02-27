"use client";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ESGEvent } from "@/types/api";
import { format } from "date-fns";
import { Leaf, Users, Shield, AlertTriangle, Filter } from "lucide-react";

const categoryIcons: Record<string, React.ReactNode> = {
  environmental: <Leaf className="w-4 h-4 text-emerald-600" />,
  social: <Users className="w-4 h-4 text-blue-600" />,
  governance: <Shield className="w-4 h-4 text-purple-600" />,
};

const severityColor = (s: number) => {
  if (s >= 8) return "destructive";
  if (s >= 5) return "warning";
  return "default";
};

export function EventTimeline({ events }: { events: ESGEvent[] }) {
  const [filter, setFilter] = useState<string>("all");
  const [severityMin, setSeverityMin] = useState<number>(1);

  const filtered = events.filter((e) => {
    if (filter !== "all" && e.category !== filter) return false;
    if (e.severity < severityMin) return false;
    return true;
  });

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">ESG Events Timeline</CardTitle>
          <div className="flex gap-1">
            {["all", "environmental", "social", "governance"].map((cat) => (
              <Button
                key={cat}
                variant={filter === cat ? "default" : "ghost"}
                size="sm"
                onClick={() => setFilter(cat)}
                className="text-xs capitalize"
              >
                {cat === "all" ? "All" : cat.slice(0, 3).toUpperCase()}
              </Button>
            ))}
            <Button
              variant={severityMin >= 5 ? "destructive" : "ghost"}
              size="sm"
              onClick={() => setSeverityMin(severityMin >= 5 ? 1 : 5)}
              className="text-xs"
            >
              <AlertTriangle className="w-3 h-3 mr-1" />
              {severityMin >= 5 ? "High" : "All"}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-80">
          {filtered.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">No events match filters</p>
          ) : (
            <div className="space-y-3">
              {filtered.map((event) => (
                <div
                  key={event.id}
                  className="flex gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {categoryIcons[event.category] || <Shield className="w-4 h-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-gray-900 line-clamp-2">{event.title}</p>
                      <Badge variant={severityColor(event.severity)} className="flex-shrink-0">
                        {event.severity}/10
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{event.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-[10px] text-gray-400">
                        {format(new Date(event.event_date), "MMM dd, yyyy HH:mm")}
                      </span>
                      <Badge variant="outline" className="text-[10px]">
                        {event.category}
                      </Badge>
                      <span
                        className={`text-[10px] font-medium ${
                          event.sentiment === "negative" ? "text-red-500" :
                          event.sentiment === "positive" ? "text-emerald-500" : "text-gray-400"
                        }`}
                      >
                        {event.sentiment}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
