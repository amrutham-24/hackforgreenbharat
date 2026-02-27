"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ESGScore } from "@/types/api";
import { Leaf, Users, Shield, TrendingDown, TrendingUp } from "lucide-react";

const riskColors: Record<string, string> = {
  low: "bg-emerald-500",
  medium: "bg-amber-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

const riskBadge: Record<string, "default" | "warning" | "destructive"> = {
  low: "default",
  medium: "warning",
  high: "destructive",
  critical: "destructive",
};

function ScoreRing({ value, label, color }: { value: number; label: string; color: string }) {
  const pct = Math.min(100, Math.max(0, value));
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-20 h-20">
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" stroke="#e5e7eb" strokeWidth="8" fill="none" />
          <circle
            cx="50" cy="50" r="40"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold">{Math.round(pct)}</span>
        </div>
      </div>
      <span className="text-xs text-gray-500 font-medium">{label}</span>
    </div>
  );
}

export function ESGScorecard({ score, companyName }: { score: ESGScore | null; companyName?: string }) {
  if (!score) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">ESG Score</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400">Select a company to view scores</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base">{companyName || "ESG Score"}</CardTitle>
            <p className="text-xs text-gray-400 mt-1">
              Updated {new Date(score.recorded_at).toLocaleDateString()}
            </p>
          </div>
          <Badge variant={riskBadge[score.risk_level] || "secondary"}>
            {score.risk_level.toUpperCase()} RISK
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-center mb-4">
          <div className="relative w-28 h-28">
            <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" stroke="#e5e7eb" strokeWidth="10" fill="none" />
              <circle
                cx="50" cy="50" r="40"
                stroke={riskColors[score.risk_level] || "#10b981"}
                strokeWidth="10"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={2 * Math.PI * 40}
                strokeDashoffset={2 * Math.PI * 40 - (score.overall / 100) * 2 * Math.PI * 40}
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold">{Math.round(score.overall)}</span>
              <span className="text-[10px] text-gray-400">OVERALL</span>
            </div>
          </div>
        </div>
        <div className="flex justify-around">
          <ScoreRing value={score.environmental} label="Environmental" color="#10b981" />
          <ScoreRing value={score.social} label="Social" color="#3b82f6" />
          <ScoreRing value={score.governance} label="Governance" color="#8b5cf6" />
        </div>
      </CardContent>
    </Card>
  );
}
