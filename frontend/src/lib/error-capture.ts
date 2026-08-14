// Global error capture for SSR

let lastCapturedError: Error | null = null;

if (typeof globalThis !== "undefined") {
  const origError = console.error;
  console.error = function (...args: any[]) {
    const err = args[0];
    if (err instanceof Error) {
      lastCapturedError = err;
    }
    return origError.apply(console, args);
  };
}

export function consumeLastCapturedError(): Error | null {
  const err = lastCapturedError;
  lastCapturedError = null;
  return err;
}
