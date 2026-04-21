import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrajectoryPlanner } from "../src/features/controls/TrajectoryPlanner";

describe("TrajectoryPlanner", () => {
  it("allows adding burns and triggers prediction", () => {
    const onPredict = vi.fn();
    render(<TrajectoryPlanner runId="test-run" onPredict={onPredict} />);
    
    fireEvent.click(screen.getByText("Add Burn"));
    fireEvent.change(screen.getByPlaceholderText("Start"), { target: { value: "1.0" } });
    fireEvent.click(screen.getByText("Plan"));
    
    expect(onPredict).toHaveBeenCalledWith([expect.objectContaining({ start_t: 1.0 })]);
  });
});
