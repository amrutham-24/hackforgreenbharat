"use client";
import { useRouter, usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import {
  LayoutDashboard,
  Building2,
  Star,
  Bell,
  Settings,
  LogOut,
  Leaf,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDashboardStore } from "@/stores/dashboard";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Watchlist", href: "/watchlist/default", icon: Star },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const logout = useAuthStore((s) => s.logout);
  const { sidebarOpen, toggleSidebar, companies, selectCompany, selectedCompanyId } = useDashboardStore();

  return (
    <aside
      className={cn(
        "flex flex-col bg-gray-900 text-white transition-all duration-300 h-screen sticky top-0",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      <div className="flex items-center gap-3 p-4 border-b border-gray-800">
        <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center flex-shrink-0">
          <Leaf className="w-5 h-5 text-white" />
        </div>
        {sidebarOpen && (
          <div className="overflow-hidden">
            <h1 className="text-sm font-bold tracking-wide">GREEN BHARAT</h1>
            <p className="text-[10px] text-gray-400">ESG Intelligence</p>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="ml-auto text-gray-400 hover:text-white hover:bg-gray-800"
          onClick={toggleSidebar}
        >
          {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </Button>
      </div>

      <nav className="flex-1 py-4 overflow-y-auto">
        <div className="px-3 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className={cn(
                "flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm transition-colors",
                pathname.startsWith(item.href)
                  ? "bg-emerald-600/20 text-emerald-400"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              )}
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </div>

        {sidebarOpen && companies.length > 0 && (
          <div className="mt-6 px-3">
            <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider px-3 mb-2">
              Companies
            </p>
            <div className="space-y-0.5 max-h-60 overflow-y-auto">
              {companies.slice(0, 15).map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    selectCompany(c.id);
                    router.push(`/company/${c.id}`);
                  }}
                  className={cn(
                    "flex items-center gap-2 w-full px-3 py-1.5 rounded-md text-xs transition-colors",
                    selectedCompanyId === c.id
                      ? "bg-gray-800 text-white"
                      : "text-gray-500 hover:text-gray-300 hover:bg-gray-800/50"
                  )}
                >
                  <Building2 className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate">{c.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      <div className="p-3 border-t border-gray-800">
        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          {sidebarOpen && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
}
