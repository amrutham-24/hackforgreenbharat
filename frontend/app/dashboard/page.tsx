"use client";
import { lazy, Suspense } from "react";

const DashboardClient = lazy(() => import("./client"));

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>}>
      <DashboardClient />
    </Suspense>
  );
}
