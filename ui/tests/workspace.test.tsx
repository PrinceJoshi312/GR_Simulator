import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Workspace } from "../src/features/workspace/Workspace";

// Mock Viewport to avoid Three.js/R3F setup issues in jsdom
vi.mock("../src/features/workspace/Viewport", () => ({
  Viewport: () => <div data-testid="mock-viewport" />
}));

// Mock EventSource for jsdom
class MockEventSource {
  onmessage = null;
  onerror = null;
  addEventListener = vi.fn();
  close = vi.fn();
  constructor(url: string) {}
}
vi.stubGlobal("EventSource", MockEventSource);

describe("Workspace", () => {
  it("shows lifecycle controls and updates state from run metadata", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValue({
        ok: true,
        json: async () => ({
          error: null,
          meta: { request_id: "req-1" },
          data: {
            run_id: "run-1",
            state: "running",
            scenario_id: "default-schwarzschild",
            seed: 42,
            g: 6.6743e-11,
            central_mass: 1.99e30,
            engine_version: "0.1.0",
            app_version: "0.1.0",
          },
        }),
      });
    
    // Customize subsequent calls for state transitions
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        error: null,
        meta: { request_id: "req-1" },
        data: {
          run_id: "run-1",
          state: "running",
          scenario_id: "default-schwarzschild",
          seed: 42,
          g: 6.6743e-11,
          central_mass: 1.99e30,
        },
      }),
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        error: null,
        meta: { request_id: "req-2" },
        data: {
          run_id: "run-1",
          state: "paused",
          scenario_id: "default-schwarzschild",
          seed: 42,
          g: 6.6743e-11,
          central_mass: 1.99e30,
        },
      }),
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        error: null,
        meta: { request_id: "req-3" },
        data: {
          run_id: "run-1",
          state: "idle",
          scenario_id: "default-schwarzschild",
          seed: 42,
          g: 6.6743e-11,
          central_mass: 1.99e30,
        },
      }),
    });

    vi.stubGlobal("fetch", fetchMock);

    render(<Workspace />);
    
    // Initial State
    expect(screen.getByText(/SYSTEM READY/i)).toBeTruthy();

    // Run
    fireEvent.click(screen.getByText("Run"));
    await waitFor(() => expect(screen.getByText(/ACTIVE SIMULATION/i)).toBeTruthy());
    expect(screen.getByText(/default-schwarzschild/i)).toBeTruthy();

    // Pause
    fireEvent.click(screen.getByText("Pause"));
    await waitFor(() => expect(screen.getByText(/SIMULATION PAUSED/i)).toBeTruthy());

    // Reset
    fireEvent.click(screen.getByText("Reset"));
    await waitFor(() => expect(screen.getByText(/SYSTEM READY/i)).toBeTruthy());
  });
});
