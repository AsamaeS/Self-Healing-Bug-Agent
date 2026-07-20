let lastCapturedError: unknown;

export function captureError(error: unknown) {
  lastCapturedError = error;
}

export function consumeLastCapturedError() {
  const captured = lastCapturedError;
  lastCapturedError = undefined;
  return captured;
}
