import type { RegistryEntry, SessionRow } from '../types'

// A tab that stopped beating shows offline, then leaves the board.
export const OFFLINE_MS = 10_000
export const FORGET_MS = 60_000

// Black text on each, so the row reads on light and dark themes alike.
const COLORS: Record<string, string> = {
  pending: '#ffd75f',
  running: '#ffd75f',
  working: '#ffd75f',
  waiting: '#87afff',
  idle: '#87afff',
  completed: '#87d787',
  complete: '#87d787',
  busy: '#ffd75f',
  failed: '#ff8787',
  killed: '#bcbcbc',
  ended: '#bcbcbc',
  offline: '#bcbcbc',
}

export const parseJson = <T,>(text: string): T | null => {
  try {
    return JSON.parse(text) as T
  } catch {
    // A tab was mid-write; its next beat replaces this.
    return null
  }
}

// Claude Code's own view of a session, for tabs that don't run this plugin yet.
const registryStatus = (entry: RegistryEntry) => {
  if (entry.parkedJobId || entry.status === undefined) {
    return 'idle'
  }

  return entry.status === 'busy' ? 'working' : entry.status
}

// Every open session gets a row; what a session published beats the registry.
export const combine = (
  published: SessionRow[],
  registry: RegistryEntry[],
  now: number,
  ttys: Map<number, string> = new Map(),
): SessionRow[] => {
  const ttyOf = (id: string) => {
    const entry = registry.find(one => one.sessionId === id)

    return entry ? ttys.get(entry.pid) : undefined
  }
  const live = published
    .filter(row => now - row.beatAt < OFFLINE_MS)
    .map(row => ({ ...row, tty: ttyOf(row.id) }))
  const unreported = registry
    .filter(entry => !live.some(row => row.id === entry.sessionId))
    .map(entry => ({
      id: entry.sessionId,
      project: entry.cwd.split('/').pop() ?? entry.cwd,
      prompt: '',
      status: registryStatus(entry),
      activity: 'No live detail (restart this session)',
      agents: [],
      beatAt: now,
      tty: ttyOf(entry.sessionId),
    }))
  const gone = published.filter(
    row =>
      !live.some(one => one.id === row.id) &&
      !registry.some(entry => entry.sessionId === row.id),
  )

  return [...live, ...unreported, ...gone].sort((a, b) =>
    a.project.localeCompare(b.project),
  )
}

export const summary = (rows: SessionRow[], now: number) => {
  const live = rows.filter(row => now - row.beatAt < OFFLINE_MS)
  const working = live.filter(row => row.status === 'working').length

  return `${working} working, ${live.length} open`
}

// A resumed session's automatic title says nothing about its work.
const RESUMED_TITLE = 'Resuming previous session'

// From a transcript's text: the person's own title, else Claude Code's newest.
export const latestTitle = (transcript: string) => {
  const entries = (transcript.match(/^\{"type":"(?:ai|custom)-title".*$/gm) ?? [])
    .flatMap(line => parseJson<{ aiTitle?: string; customTitle?: string }>(line) ?? [])
  const custom = entries.findLast(entry => entry.customTitle)?.customTitle
  const automatic = entries.findLast(
    entry => entry.aiTitle && entry.aiTitle !== RESUMED_TITLE,
  )?.aiTitle

  return custom ?? automatic
}

// One line of what a session is about: its title, else its prompt's opening.
export const description = (row: SessionRow, title?: string) =>
  title || row.prompt.trim().split('\n')[0] || 'No prompt yet'

const clip = (text: string, width: number) => {
  const flat = text.replace(/\s+/g, ' ').trim()

  return flat.length > width ? `${flat.slice(0, Math.max(0, width - 1))}…` : flat
}

const badge = (status: string) => {
  const [r, g, b] = (COLORS[status] ?? '#bcbcbc')
    .slice(1)
    .match(/../g)!
    .map(hex => parseInt(hex, 16))

  return `\x1b[48;2;${r};${g};${b}m\x1b[38;2;0;0;0m ${status.toUpperCase()} \x1b[0m`
}

const dim = (text: string) => `\x1b[2m${text}\x1b[0m`
const bold = (text: string) => `\x1b[1m${text}\x1b[0m`

// Sessions a digit key can jump to, numbered as the board shows them.
export const jumpable = (rows: SessionRow[]) =>
  rows.filter(row => row.tty?.startsWith('ttys')).slice(0, 9)

export const renderHub = (
  rows: SessionRow[],
  titles: Map<string, string>,
  now: number,
  { columns, height }: { columns: number; height: number },
) => {
  const keys = jumpable(rows)
  const body = rows.length === 0 ? [dim('No Claude sessions open.')] : []
  const projects = [...new Set(rows.map(row => row.project))]

  for (const project of projects) {
    body.push(bold(project))

    for (const row of rows.filter(one => one.project === project)) {
      const status = now - row.beatAt < OFFLINE_MS ? row.status : 'offline'
      const key = keys.indexOf(row) + 1

      body.push(
        `  ${key > 0 ? `${key} ` : '  '}${badge(status)} ${clip(
          description(row, titles.get(row.id)),
          columns - status.length - 8,
        )}`,
        `      ${dim(clip(row.activity, columns - 6))}`,
      )

      for (const agent of row.agents) {
        body.push(
          `      ${badge(agent.status)} ${clip(
            `${agent.label}: ${agent.activity} (${agent.tools} tool calls)`,
            columns - agent.status.length - 10,
          )}`,
        )
      }
    }

    body.push('')
  }

  // Header, its gap and the footer always show; the board gives way below them.
  const room = Math.max(0, height - 3)
  const fits = body.length <= room
  const shown = fits ? body : body.slice(0, Math.max(0, room - 1))
  const hidden = body.length - shown.length

  return [
    `${bold('Quarterback')}  ${dim(summary(rows, now))}`,
    '',
    ...shown,
    ...(fits ? [] : [dim(`… ${hidden} more lines, enlarge the window`)]),
    dim('1-9 go to session · q quit'),
  ]
}
