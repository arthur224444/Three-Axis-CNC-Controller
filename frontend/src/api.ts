export type HealthStatus = {
  status: string;
  serial_open: boolean;
  simulator: boolean;
  port: string;
  message: string;
};

export type CommandResult = {
  httpStatus: number;
  success: boolean;
  message: string;
  frames_sent: string[];
  commands_executed: number | null;
  failing_frame_index: number | null;
  error: string | null;
  unauthorized: boolean;
};

function passphraseHeaders(passphrase: string, json: boolean): HeadersInit {
  const headers: Record<string, string> = {
    "X-CNC-Passphrase": passphrase,
  };
  if (json) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

function messageFromBody(body: unknown, fallback: string): string {
  if (body !== null && typeof body === "object") {
    const record = body as Record<string, unknown>;
    if (typeof record.message === "string" && record.message.length > 0) {
      return record.message;
    }
    if (typeof record.detail === "string" && record.detail.length > 0) {
      return record.detail;
    }
    if (Array.isArray(record.detail) && record.detail.length > 0) {
      const first = record.detail[0] as { msg?: unknown };
      if (typeof first?.msg === "string") {
        return first.msg;
      }
    }
  }
  return fallback;
}

function resultFromBody(httpStatus: number, body: unknown, fallback: string): CommandResult {
  const record =
    body !== null && typeof body === "object"
      ? (body as Record<string, unknown>)
      : {};
  const frames = Array.isArray(record.frames_sent)
    ? record.frames_sent.filter((item): item is string => typeof item === "string")
    : [];
  const executed =
    typeof record.commands_executed === "number" ? record.commands_executed : null;
  const failing =
    typeof record.failing_frame_index === "number" ? record.failing_frame_index : null;
  const error = typeof record.error === "string" ? record.error : null;
  return {
    httpStatus,
    success: record.success === true,
    message: messageFromBody(body, fallback),
    frames_sent: frames,
    commands_executed: executed,
    failing_frame_index: failing,
    error,
    unauthorized: httpStatus === 401,
  };
}

async function readBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (text === "") {
    return null;
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return { message: text };
  }
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch("/health");
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return (await response.json()) as HealthStatus;
}

export async function postSingleCommand(
  path: string,
  passphrase: string,
  repeat: number,
): Promise<CommandResult> {
  const sendBody = repeat !== 1;
  const response = await fetch(path, {
    method: "POST",
    headers: passphraseHeaders(passphrase, sendBody),
    body: sendBody ? JSON.stringify({ repeat }) : undefined,
  });
  const body = await readBody(response);
  return resultFromBody(response.status, body, response.statusText);
}

export async function postBatchCommands(
  commands: string,
  passphrase: string,
): Promise<CommandResult> {
  const response = await fetch("/commands", {
    method: "POST",
    headers: passphraseHeaders(passphrase, true),
    body: JSON.stringify({ commands }),
  });
  const body = await readBody(response);
  return resultFromBody(response.status, body, response.statusText);
}
