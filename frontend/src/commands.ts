/** Firmware alphabet. Letter case is significant. */
export const PROTOCOL_ALPHABET = "XxYyZzAaBbCcSsERn";

export type CommandDef = {
  letter: string;
  label: string;
  path: string;
};

export const JOG: CommandDef[] = [
  { letter: "x", label: "Step X negative (x)", path: "/axis/x/backward" },
  { letter: "X", label: "Step X positive (X)", path: "/axis/x/forward" },
  { letter: "y", label: "Step Y negative (y)", path: "/axis/y/backward" },
  { letter: "Y", label: "Step Y positive (Y)", path: "/axis/y/forward" },
  { letter: "z", label: "Step Z negative (z)", path: "/axis/z/backward" },
  { letter: "Z", label: "Step Z positive (Z)", path: "/axis/z/forward" },
];

export const FORCED: CommandDef[] = [
  { letter: "a", label: "Force step X negative (a)", path: "/axis/x/backward/forced" },
  { letter: "A", label: "Force step X positive (A)", path: "/axis/x/forward/forced" },
  { letter: "b", label: "Force step Y negative (b)", path: "/axis/y/backward/forced" },
  { letter: "B", label: "Force step Y positive (B)", path: "/axis/y/forward/forced" },
  { letter: "c", label: "Force step Z negative (c)", path: "/axis/z/backward/forced" },
  { letter: "C", label: "Force step Z positive (C)", path: "/axis/z/forward/forced" },
];

export const SPINDLE_ON: CommandDef = {
  letter: "S",
  label: "Spindle on (S)",
  path: "/spindle/on",
};

export const SPINDLE_OFF: CommandDef = {
  letter: "s",
  label: "Spindle off (s)",
  path: "/spindle/off",
};

export const ESTOP_TRIGGER: CommandDef = {
  letter: "E",
  label: "Emergency stop (E)",
  path: "/emergency-stop",
};

export const ESTOP_RESET: CommandDef = {
  letter: "R",
  label: "Reset emergency stop (R)",
  path: "/emergency-stop/reset",
};

export const NOOP: CommandDef = {
  letter: "n",
  label: "Padding / no-op (n)",
  path: "/noop",
};

export type InvalidChar = {
  character: string;
  index: number;
};

export function findInvalidCommandChar(commands: string): InvalidChar | null {
  for (let index = 0; index < commands.length; index += 1) {
    const character = commands[index];
    if (!PROTOCOL_ALPHABET.includes(character)) {
      return { character, index };
    }
  }
  return null;
}

export function axisPairs(defs: CommandDef[]): [CommandDef, CommandDef][] {
  const pairs: [CommandDef, CommandDef][] = [];
  for (let i = 0; i < defs.length; i += 2) {
    pairs.push([defs[i], defs[i + 1]]);
  }
  return pairs;
}
