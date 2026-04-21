export type RunState = "idle" | "loading" | "running" | "warning" | "error" | "paused";

export type RunPayload = {
  run_id: string;
  state: RunState;
  scenario_id: string;
  seed: number;
  g: number;
  central_mass: number;
  angular_momentum: number;
  engine_version: string;
  app_version: string;
  objects: Array<{
    name: string;
    mass: number;
    state: { x: number; y: number; vx: number; vy: number };
  }>;
};

const BASE_URL = "http://127.0.0.1:8000";

type Envelope<T> = {
  data: T | null;
  meta: { request_id: string };
  error: { code: string; message: string; context: Record<string, unknown>; hint?: string } | null;
};

async function parseEnvelope(response: Response): Promise<RunPayload> {
  const payload = (await response.json()) as Envelope<RunPayload>;
  if (!response.ok || payload.error || !payload.data) {
    throw new Error(payload.error?.message ?? "Request failed");
  }
  return payload.data;
}

export async function createRun(scenarioId: string = "solar-system"): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario_id: scenarioId, seed: 42 }),
  });
  return parseEnvelope(response);
}

export async function pauseRun(runId: string): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/pause`, { method: "POST" });
  return parseEnvelope(response);
}

export async function resetRun(runId: string): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/reset`, { method: "POST" });
  return parseEnvelope(response);
}

export async function updateRuntimeParams(
  runId: string,
  params: { timestep: number; g: number; central_mass: number; angular_momentum: number }
): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/params`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return parseEnvelope(response);
}

export async function addCatalogObject(runId: string, objectName: string): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/objects/catalog/${objectName}`, {
    method: "POST",
  });
  return parseEnvelope(response);
}

export async function addCustomObject(
  runId: string,
  params: { name: string; mass: number; x: number; y: number; vx: number; vy: number }
): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/objects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return parseEnvelope(response);
}

export async function removeObject(runId: string, name: string): Promise<RunPayload> {
  const response = await fetch(`${BASE_URL}/runs/${runId}/objects/${name}`, {
    method: "DELETE",
  });
  return parseEnvelope(response);
}
