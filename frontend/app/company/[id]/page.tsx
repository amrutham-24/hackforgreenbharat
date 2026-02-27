"use client";
import { lazy, Suspense } from "react";

const CompanyClient = lazy(() => import("./client"));

export default function CompanyPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>}>
      <CompanyClient />
    </Suspense>
  );
}
