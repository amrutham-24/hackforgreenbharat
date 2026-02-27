"use client";
import { lazy, Suspense } from "react";

const WatchlistClient = lazy(() => import("./client"));

export default function WatchlistPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>}>
      <WatchlistClient />
    </Suspense>
  );
}
