export type AgentRow = {
  id: string
  label: string
  type: string
  status: string
  activity: string
  tools: number
}

// One Claude Code session, as it publishes itself for the other tabs to read.
export type SessionRow = {
  id: string
  project: string
  prompt: string
  status: string
  activity: string
  agents: AgentRow[]
  beatAt: number
  tty?: string
}

// The fields used from Claude Code's registry, ~/.claude/sessions/<pid>.json.
export type RegistryEntry = {
  pid: number
  sessionId: string
  cwd: string
  name?: string
  status?: string
  parkedJobId?: string
}

declare module 'claude-code' {
  interface PluginState {
    quarterback: {
      self: Shaped<SessionRow | null>
    }
  }
}
