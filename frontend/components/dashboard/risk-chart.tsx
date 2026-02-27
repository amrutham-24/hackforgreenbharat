"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ESGScore } from "@/types/api";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { format } from "date-fns";

export function RiskChart({ scores }: { scores: ESGScore[] }) {
  const data = scores.map((s) => ({
    date: format(new Date(s.recorded_at), "MMM dd"),
    Overall: Math.round(s.overall * 10) / 10,
    Environmental: Math.round(s.environmental * 10) / 10,
    Social: Math.round(s.social * 10) / 10,
    Governance: Math.round(s.governance * 10) / 10,
  }));

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Risk Trend</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400">No score data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Risk Trend (30 Days)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorOverall" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorEnv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Area
                type="monotone"
                dataKey="Overall"
                stroke="#10b981"
                strokeWidth={2}
                fill="url(#colorOverall)"
              />
              <Area
                type="monotone"
                dataKey="Environmental"
                stroke="#059669"
                strokeWidth={1.5}
                fill="url(#colorEnv)"
                strokeDasharray="4 4"
              />
              <Area
                type="monotone"
                dataKey="Social"
                stroke="#3b82f6"
                strokeWidth={1.5}
                fill="none"
                strokeDasharray="4 4"
              />
              <Area
                type="monotone"
                dataKey="Governance"
                stroke="#8b5cf6"
                strokeWidth={1.5}
                fill="none"
                strokeDasharray="4 4"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
