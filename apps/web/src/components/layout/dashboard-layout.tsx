import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";
import { PageContainer } from "./page-container";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
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
