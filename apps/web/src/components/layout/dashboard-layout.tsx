import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";
import { StatusBar } from "./status-bar";
import { PageContainer } from "./page-container";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <StatusBar />
      <Sidebar />
      <div className="lg:pl-(--sidebar-width)">
        <TopBar />
        <main>
          <PageContainer>{children}</PageContainer>
        </main>
      </div>
    </div>
  );
}
