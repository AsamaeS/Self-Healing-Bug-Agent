const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Ensure VITE_API_URL is available
if (!import.meta.env.VITE_API_URL) {
  console.warn("VITE_API_URL is not set. Using default:", API_BASE_URL);
}

export { API_BASE_URL };

export interface CreateRunRequest {
  repo_full_name: string;
  base_sha: string;
  bug_report: string;
  trigger_type?: string;
}

export interface AcceptedRun {
  run_id: string;
  status: string;
}

export interface RepairRun {
  id: string;
  repo_full_name: string;
  trigger_type: string;
  base_sha: string;
  bug_report: string;
  issue_number?: number;
  workflow_run_id?: number;
  status: string;
  iteration: number;
  max_iterations: number;
  events: Array<{
    status: string;
    message: string;
    created_at: string;
    metadata?: Record<string, any>;
  }>;
  verification?: any;
  pull_request_url?: string;
  created_at: string;
  updated_at: string;
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Failed to fetch health");
  }
  return response.json();
}

export async function createRun(data: CreateRunRequest): Promise<AcceptedRun> {
  const response = await fetch(`${API_BASE_URL}/api/v1/runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Failed to create run");
  }
  return response.json();
}

export async function getRuns(): Promise<RepairRun[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/runs`);
  if (!response.ok) {
    throw new Error("Failed to fetch runs");
  }
  return response.json();
}

export async function getRun(runId: string): Promise<RepairRun> {
  const response = await fetch(`${API_BASE_URL}/api/v1/runs/${runId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch run");
  }
  return response.json();
}
