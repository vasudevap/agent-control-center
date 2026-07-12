import { DashboardLayout } from "@/components/layout/dashboard-layout";

export default function ShellLayout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
