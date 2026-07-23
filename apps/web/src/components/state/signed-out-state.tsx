import { ErrorState } from "@/components/state/error-state";
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
      <ErrorState
        title="Owner sign-in required"
        description={description}
        className="py-12"
      />
      {signInUrl && (
        <div className="flex justify-center pb-6">
          <Button asChild>
            <a href={signInUrl}>
              <GoogleLogo />
              Sign in with Google
            </a>
          </Button>
        </div>
      )}
    </Card>
  );
}
