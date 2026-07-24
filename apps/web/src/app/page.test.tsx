import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import LandingPage from "./page";

const API_BASE_URL = "https://api.atlas.example.test";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("LandingPage", () => {
  it("positions Atlas as the landing page and links login to owner sign-in", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", API_BASE_URL);

    render(<LandingPage />);

    expect(screen.getByRole("heading", { level: 1, name: "Atlas" })).toBeInTheDocument();
    expect(
      screen.getByText(/known, trusted, connected, healthy, failing/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/does not host, schedule, execute, pause, resume, or stop/i),
    ).toBeInTheDocument();
    expect(await screen.findAllByRole("link", { name: "Sign in with Google" })).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          href: `${API_BASE_URL}/auth/owner/google/start`,
        }),
      ]),
    );
    expect(screen.getAllByRole("link", { name: /Preview control center/i })[0]).toHaveAttribute(
      "href",
      "/control-center",
    );
  });
});
