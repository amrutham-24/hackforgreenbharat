"use client";
import { lazy, Suspense } from "react";

const SettingsClient = lazy(() => import("./client"));

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>}>
      <SettingsClient />
    </Suspense>
  );
}
