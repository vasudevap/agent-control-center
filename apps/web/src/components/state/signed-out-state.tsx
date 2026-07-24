import { LogIn } from "lucide-react";
import { EmptyState } from "@/components/state/empty-state";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { dashboardSignInUrl } from "@/lib/dashboard-runtime";
import { GoogleLogo } from "@/components/brand/google-logo";

export interface SignedOutStateProps {
  description: string;
}

export function SignedOutState({ description }: SignedOutStateProps) {
  const signInUrl = dashboardSignInUrl();

  return (
    <Card>
      <EmptyState
        icon={LogIn}
        title="Owner sign-in required"
        description={description}
        className="py-12"
        action={
          signInUrl ? (
            <Button asChild>
              <a href={signInUrl}>
                <GoogleLogo />
                Sign in with Google
              </a>
            </Button>
          ) : undefined
        }
      />
    </Card>
  );
}
