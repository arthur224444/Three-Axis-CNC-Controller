const STORAGE_KEY = "cnc-passphrase";

export function loadPassphrase(): string | null {
  try {
    const value = sessionStorage.getItem(STORAGE_KEY);
    if (value === null || value === "") {
      return null;
    }
    return value;
  } catch {
    return null;
  }
}

export function savePassphrase(value: string): void {
  sessionStorage.setItem(STORAGE_KEY, value);
}

export function clearPassphrase(): void {
  sessionStorage.removeItem(STORAGE_KEY);
}
