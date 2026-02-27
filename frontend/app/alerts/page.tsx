"use client";
import { lazy, Suspense } from "react";

const AlertsClient = lazy(() => import("./client"));

export default function AlertsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>}>
      <AlertsClient />
    </Suspense>
  );
}
