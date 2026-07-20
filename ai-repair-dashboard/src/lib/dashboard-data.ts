export const metrics = {
  currentRunStatus: "Completed",
  repairAgentStatus: "Fixed",
  sandboxVerificationStatus: "Verified",
  confidenceScore: 96,
  retryCounter: "0 / 3",
  pullRequestStatus: "Opened",
};

export const repoInfo = {
  status: "Connected",
  name: "demo/calculator",
  owner: "Hackathon Team",
  branch: "repair/calculator-value-error",
  lastCommit: "abcdef1",
  language: "Python",
};

export const issueInfo = {
  priority: "High",
  number: 42,
  bugType: "Runtime error",
  title: "divide(10, 0) raises the wrong exception",
  description:
    "The public contract requires ValueError for a zero divisor, but the current implementation leaks Python's ZeroDivisionError.",
  filePath: "calculator.py",
};

export const attempt = {
  current: 1,
  total: 3,
  elapsed: "00:02",
  stage: "Verified green",
  progress: 100,
};

export const patchDiff = [
  { type: "meta", text: "@@ def divide(a, b):" },
  { type: "add", text: "    if b == 0:" },
  { type: "add", text: '        raise ValueError("Cannot divide by zero")' },
  { type: "ctx", text: "    return a / b" },
] as const;

export const testResults = [
  { name: "regression test fails before patch", duration: "0.21s", status: "PASS" },
  { name: "test_divide_by_zero_raises_error", duration: "0.18s", status: "PASS" },
  { name: "full pytest suite", duration: "0.34s", status: "PASS" },
];

export const verification = [
  { label: "Bug reproduced", value: "Yes", ok: true },
  { label: "Pre-patch test", value: "Failed", ok: true },
  { label: "Patch applied", value: "Yes", ok: true },
  { label: "Targeted test", value: "Passed", ok: true },
  { label: "Full suite", value: "Passed", ok: true },
  { label: "PR gate", value: "Open", ok: true },
];

export const workflowSteps = [
  { label: "Receive bug report", status: "done" },
  { label: "Reproduce failure", status: "done" },
  { label: "Diagnose and propose patch", status: "done" },
  { label: "Generate regression test", status: "done" },
  { label: "Prove test fails pre-patch", status: "done" },
  { label: "Run full suite post-patch", status: "done" },
  { label: "Open verified PR", status: "done" },
] as const;

export const initialLogs = [
  { t: "10:00:00", level: "info", msg: "Webhook accepted for demo/calculator" },
  { t: "10:00:01", level: "error", msg: "Reproduced ZeroDivisionError on original code" },
  { t: "10:00:01", level: "info", msg: "Repair agent proposed a one-file patch" },
];

export const streamLogs = [
  { level: "success", msg: "Regression test failed against original code as required" },
  { level: "success", msg: "Patch applied in disposable sandbox" },
  { level: "success", msg: "Full test suite passed" },
  { level: "success", msg: "Verification gate opened; pull request created" },
];
