import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  fetchHealth,
  postBatchCommands,
  postSingleCommand,
  type CommandResult,
  type HealthStatus,
} from "./api";
import {
  ESTOP_RESET,
  FORCED,
  JOG,
  NOOP,
  PROTOCOL_ALPHABET,
  SPINDLE_OFF,
  SPINDLE_ON,
  axisPairs,
  findInvalidCommandChar,
  type CommandDef,
} from "./commands";
import { clearPassphrase, loadPassphrase, savePassphrase } from "./passphrase";

const HEALTH_POLL_MS = 4000;

function healthClass(health: HealthStatus | null, unreachable: boolean): string {
  if (unreachable || health === null) {
    return "health health-unknown";
  }
  if (health.status === "degraded") {
    return "health health-degraded";
  }
  return "health health-ok";
}

function healthLabel(health: HealthStatus | null, unreachable: boolean): string {
  if (unreachable) {
    return "API unreachable";
  }
  if (health === null) {
    return "Checking connection…";
  }
  if (health.simulator) {
    return `Simulator · ${health.status}`;
  }
  if (health.serial_open) {
    return `Serial open · ${health.port}`;
  }
  return `Degraded · ${health.port}`;
}

function PassphraseGate({
  error,
  onUnlock,
}: {
  error: string | null;
  onUnlock: () => void;
}) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = value;
    if (trimmed === "") {
      return;
    }
    savePassphrase(trimmed);
    setValue("");
    onUnlock();
  }

  return (
    <main className="gate">
      <h1>CNC Controller</h1>
      <p className="gate-note">
        Enter the CNC API passphrase (<code>CNC_PASSPHRASE</code> / header{" "}
        <code>X-CNC-Passphrase</code>). It is stored for this browser tab only
        and is never put in the URL.
      </p>
      <form className="gate-form" onSubmit={handleSubmit} autoComplete="off">
        <label className="sr-only" htmlFor="passphrase">
          Passphrase
        </label>
        <input
          id="passphrase"
          type="password"
          name="passphrase"
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Passphrase"
        />
        <button type="submit" className="btn btn-primary" disabled={value === ""}>
          Unlock
        </button>
      </form>
      {error !== null ? <p className="error-banner">{error}</p> : null}
    </main>
  );
}

function CommandButton({
  command,
  disabled,
  className,
  onSend,
}: {
  command: CommandDef;
  disabled: boolean;
  className: string;
  onSend: (command: CommandDef) => void;
}) {
  return (
    <button
      type="button"
      className={className}
      disabled={disabled}
      onClick={() => onSend(command)}
    >
      {command.label}
    </button>
  );
}

function AxisRows({
  defs,
  disabled,
  buttonClass,
  onSend,
}: {
  defs: CommandDef[];
  disabled: boolean;
  buttonClass: string;
  onSend: (command: CommandDef) => void;
}) {
  return (
    <div className="axis-rows">
      {axisPairs(defs).map(([negative, positive]) => (
        <div className="axis-row" key={negative.letter + positive.letter}>
          <CommandButton
            command={negative}
            disabled={disabled}
            className={buttonClass}
            onSend={onSend}
          />
          <CommandButton
            command={positive}
            disabled={disabled}
            className={buttonClass}
            onSend={onSend}
          />
        </div>
      ))}
    </div>
  );
}

function ResultPanel({ result, busy }: { result: CommandResult | null; busy: boolean }) {
  if (busy) {
    return (
      <section className="result result-busy" aria-live="polite">
        <strong>In flight</strong>
        <p>Waiting for the machine. Controls are locked until this finishes.</p>
      </section>
    );
  }
  if (result === null) {
    return null;
  }
  const tone = result.success ? "result-ok" : "result-fail";
  return (
    <section className={`result ${tone}`} aria-live="polite">
      <strong>
        HTTP {result.httpStatus}
        {result.success ? " · success" : " · failed"}
        {result.error !== null ? ` · ${result.error}` : ""}
      </strong>
      <p>{result.message}</p>
      {result.commands_executed !== null ? (
        <p>commands_executed: {result.commands_executed}</p>
      ) : null}
      {result.failing_frame_index !== null ? (
        <p>failing_frame_index: {result.failing_frame_index}</p>
      ) : null}
      {result.frames_sent.length > 0 ? (
        <p className="frames">
          frames_sent:{" "}
          {result.frames_sent.map((frame, index) => (
            <code key={`${index}-${frame}`}>{frame}</code>
          ))}
        </p>
      ) : null}
    </section>
  );
}

export default function App() {
  const [unlocked, setUnlocked] = useState(() => loadPassphrase() !== null);
  const [gateError, setGateError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthUnreachable, setHealthUnreachable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<CommandResult | null>(null);
  const [repeat, setRepeat] = useState(1);
  const [commandString, setCommandString] = useState("");
  const [commandWarn, setCommandWarn] = useState<string | null>(null);

  const refreshHealth = useCallback(async () => {
    try {
      const next = await fetchHealth();
      setHealth(next);
      setHealthUnreachable(false);
    } catch {
      setHealthUnreachable(true);
    }
  }, []);

  useEffect(() => {
    void refreshHealth();
    const id = window.setInterval(() => {
      void refreshHealth();
    }, HEALTH_POLL_MS);
    return () => window.clearInterval(id);
  }, [refreshHealth]);

  function lockoutFrom401(next: CommandResult) {
    clearPassphrase();
    setUnlocked(false);
    setGateError(
      next.message !== ""
        ? `Passphrase rejected. ${next.message}`
        : "Passphrase rejected.",
    );
    setResult(next);
  }

  async function runCommand(send: (passphrase: string) => Promise<CommandResult>) {
    const passphrase = loadPassphrase();
    if (passphrase === null) {
      setUnlocked(false);
      setGateError("Passphrase is missing. Enter it again.");
      return;
    }
    setBusy(true);
    setCommandWarn(null);
    try {
      const next = await send(passphrase);
      if (next.unauthorized) {
        lockoutFrom401(next);
        return;
      }
      setResult(next);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Request failed";
      setResult({
        httpStatus: 0,
        success: false,
        message,
        frames_sent: [],
        commands_executed: null,
        failing_frame_index: null,
        error: "network",
        unauthorized: false,
      });
    } finally {
      setBusy(false);
    }
  }

  function handleSingle(command: CommandDef) {
    void runCommand((passphrase) => postSingleCommand(command.path, passphrase, repeat));
  }

  function handleBatch() {
    const commands = commandString;
    if (commands.length === 0) {
      setCommandWarn("Command string is empty.");
      return;
    }
    const invalid = findInvalidCommandChar(commands);
    if (invalid !== null) {
      setCommandWarn(
        `Invalid character ${JSON.stringify(invalid.character)} at index ${invalid.index}. Allowed: ${PROTOCOL_ALPHABET}`,
      );
      return;
    }
    void runCommand((passphrase) => postBatchCommands(commands, passphrase));
  }

  function handleForget() {
    clearPassphrase();
    setUnlocked(false);
    setGateError(null);
    setResult(null);
  }

  if (!unlocked) {
    return (
      <>
        <p className={`gate-health ${healthClass(health, healthUnreachable)}`}>
          {healthLabel(health, healthUnreachable)}
        </p>
        <PassphraseGate
          error={gateError}
          onUnlock={() => {
            setGateError(null);
            setResult(null);
            setUnlocked(true);
          }}
        />
      </>
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>CNC Controller</h1>
          <p className={healthClass(health, healthUnreachable)} title={health?.message}>
            {healthLabel(health, healthUnreachable)}
          </p>
        </div>
        <button type="button" className="btn btn-ghost" onClick={handleForget}>
          Forget passphrase
        </button>
      </header>

      <ResultPanel result={result} busy={busy} />

      <section className="panel">
        <h2>Jog</h2>
        <p className="hint">Normal steps. Blocked while emergency stop is latched.</p>
        <AxisRows
          defs={JOG}
          disabled={busy}
          buttonClass="btn btn-jog"
          onSend={handleSingle}
        />
      </section>

      <section className="panel panel-forced">
        <h2>Forced override</h2>
        <p className="hint">
          Ignores emergency stop. Use to jog off a tripped limit — not for normal
          moves.
        </p>
        <AxisRows
          defs={FORCED}
          disabled={busy}
          buttonClass="btn btn-forced"
          onSend={handleSingle}
        />
      </section>

      <div className="hazard-gap" />

      <section className="panel panel-spindle">
        <h2>Spindle</h2>
        <p className="hint">Separated from jogs so these are harder to tap by accident.</p>
        <div className="hazard-row">
          <CommandButton
            command={SPINDLE_OFF}
            disabled={busy}
            className="btn btn-spindle-off"
            onSend={handleSingle}
          />
          <CommandButton
            command={SPINDLE_ON}
            disabled={busy}
            className="btn btn-spindle-on"
            onSend={handleSingle}
          />
        </div>
      </section>

      <section className="panel panel-estop">
        <h2>Emergency stop</h2>
        <p className="hint">Clears the firmware e-stop latch so normal jogs can resume.</p>
        <CommandButton
          command={ESTOP_RESET}
          disabled={busy}
          className="btn btn-estop"
          onSend={handleSingle}
        />
      </section>

      <section className="panel">
        <h2>No-op</h2>
        <CommandButton
          command={NOOP}
          disabled={busy}
          className="btn btn-noop"
          onSend={handleSingle}
        />
      </section>

      <section className="panel">
        <h2>Repeat</h2>
        <p className="hint">Applies to the single-command buttons above (1–100), not the string.</p>
        <label className="repeat">
          <span>Times</span>
          <input
            type="number"
            min={1}
            max={100}
            inputMode="numeric"
            disabled={busy}
            value={repeat}
            onChange={(event) => {
              const parsed = Number.parseInt(event.target.value, 10);
              if (!Number.isFinite(parsed)) {
                setRepeat(1);
                return;
              }
              setRepeat(Math.min(100, Math.max(1, parsed)));
            }}
          />
        </label>
      </section>

      <section className="panel">
        <h2>Command string</h2>
        <p className="hint">
          Alphabet <code>{PROTOCOL_ALPHABET}</code> (case-sensitive). Sent as{" "}
          <code>POST /commands</code>.
        </p>
        <textarea
          className="command-input"
          rows={3}
          disabled={busy}
          value={commandString}
          spellCheck={false}
          autoCapitalize="off"
          autoCorrect="off"
          autoComplete="off"
          placeholder="e.g. XYzzxxxZZZZZ"
          onChange={(event) => {
            setCommandString(event.target.value);
            setCommandWarn(null);
          }}
        />
        {commandWarn !== null ? <p className="error-banner">{commandWarn}</p> : null}
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy}
          onClick={handleBatch}
        >
          Send
        </button>
      </section>
    </div>
  );
}
