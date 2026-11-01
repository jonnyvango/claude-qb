import { atom, read, update } from 'claude-code'
import type { AgentInfo, Register } from 'claude-code'

import type { AgentRow, RegistryEntry, SessionRow } from '../types'
import { combine, FORGET_MS, parseJson, summary } from './board'

const BEAT_MS = 2000
const self = atom({ plugin: 'quarterback', key: 'self' } as const, null, {
  shape: 'self-1',
})

// Dark tints for the terminal's own background, so its text stays readable.
const TAB_TINTS: Record<string, string> = {
  working: '#3a3000',
  complete: '#0f2e14',
}
const ACTIVE = ['pending', 'running', 'waiting']

// The hub is its own program in its own window, so no session UI surrounds it.
// Interactive, as a fresh window's PATH comes from .zshrc.
const OPEN_HUB = `tell application "Ghostty"
  set config to new surface configuration
  set command of config to "/bin/zsh -ilc qb"
  new window with configuration config
  activate
end tell`

// Walks up from this child to the first ancestor holding a terminal.
const FIND_TTY = `p=$PPID
while [ "$p" -gt 1 ]; do
  t=$(ps -o tty= -p "$p" | tr -d ' ')
  case "$t" in
    ''|'??') p=$(ps -o ppid= -p "$p" | tr -d ' ') ;;
    *) echo "$t"; exit ;;
  esac
done`

// The input field that best says what a call is doing, by tool.
const describe = (e: object & { tool: string }) => {
  const input = e as unknown as Record<string, unknown>
  const detail = ['command', 'file_path', 'pattern', 'url', 'query', 'description']
    .map(field => input[field])
    .find(value => typeof value === 'string')

  return detail ? `${e.tool}: ${detail}` : e.tool
}

const merge = (rows: AgentRow[], live: AgentInfo[]) => {
  const merged = rows.map(row => {
    const info = live.find(one => one.id === row.id)
    // The engine drops a finished agent's task; the row stays on the board.
    const status = info?.status ?? (ACTIVE.includes(row.status) ? 'ended' : row.status)

    return status === row.status ? row : { ...row, status }
  })
  const added = live
    .filter(info => !rows.some(row => row.id === info.id))
    .map(info => ({
      id: info.id,
      label: info.name ?? info.description,
      type: info.type,
      status: info.status,
      activity: info.description,
      tools: 0,
    }))

  return [...merged, ...added]
}

export const register: Register = on => {
  let dir = ''
  let registryDir = ''
  let tty = ''
  let paintedStatus = ''

  on('session.start', async ($, e, next) => {
    const started = await next(e)
    const id = await $.session.id()
    const sh = (script: string) => $.process.run(['sh', '-c', script])
    const home = (await sh('echo "$HOME"')).stdout.trim()
    dir = `${home}/.claude/quarterback`
    registryDir = `${home}/.claude/sessions`
    tty = (await sh(FIND_TTY)).stdout.trim()
    await sh(`mkdir -p "${dir}"`)

    const project = e.cwd.split('/').pop() ?? e.cwd
    const existing = await read($, self)
    await update($, self, () =>
      existing ?? {
        id,
        project,
        prompt: '',
        status: 'complete',
        activity: 'Waiting for a prompt',
        agents: [],
        beatAt: 0,
      },
    )
    await $.command.register({
      name: 'qb',
      description: 'Open the hub of every Claude session in its own window',
    })

    $.clock.every(BEAT_MS, async () => {
      const now = await $.clock.now()
      const mine = await read($, self)

      if (!mine) {
        return
      }

      const published = {
        ...mine,
        agents: merge(mine.agents, await $.agent.list()),
        beatAt: now,
      }
      await update($, self, () => published)
      await $.fs.write(`${dir}/${id}.json`, JSON.stringify(published))

      if (tty && paintedStatus !== published.status) {
        paintedStatus = published.status
        const osc = `\\033]11;${TAB_TINTS[published.status]}\\007`
        await sh(`printf '${osc}' > /dev/${tty}`)
      }

      const entries = await $.fs.list(dir)
      const files = await Promise.all(
        entries
          .filter(entry => entry.name.endsWith('.json'))
          .map(entry => $.fs.read(`${dir}/${entry.name}`)),
      )
      const rows = files.flatMap(text => parseJson<SessionRow>(text) ?? [])
      const stale = rows.filter(row => now - row.beatAt > FORGET_MS)

      if (stale.length > 0) {
        await $.process.run(['rm', '-f', ...stale.map(row => `${dir}/${row.id}.json`)])
      }

      // Only the .json files: the .key files beside them are secrets.
      const registryFiles = await $.fs.list(registryDir)
      const registry = (
        await Promise.all(
          registryFiles
            .filter(entry => entry.name.endsWith('.json'))
            .map(entry => $.fs.read(`${registryDir}/${entry.name}`)),
        )
      ).flatMap(text => parseJson<RegistryEntry>(text) ?? [])
      // A crashed session leaves its file behind; ps says which pids are real.
      const pids = registry.map(entry => entry.pid).join(',')
      const ps = await $.process.run(['ps', '-o', 'pid=,tty=', '-p', pids])
      const ttys = new Map(
        ps.stdout
          .split('\n')
          .map(line => line.trim().split(/\s+/))
          .map(([pid, device]) => [Number(pid), device ?? ''] as const),
      )
      const open = registry.filter(entry => ttys.has(entry.pid))

      const kept = combine(
        rows.filter(row => now - row.beatAt <= FORGET_MS),
        open,
        now,
        ttys,
      )
      $.ui.status(`QB: ${summary(kept, now)}`)
    })

    return started
  })

  on('session.end', async ($, e, next) => {
    const mine = await read($, self)

    if (mine && dir) {
      await $.process.run(['rm', '-f', `${dir}/${mine.id}.json`])
    }
    if (tty) {
      await $.process.run(['sh', '-c', `printf '\\033]111\\007' > /dev/${tty}`])
    }

    return next(e)
  })

  on('command.run', { command: 'qb' }, async $ => {
    const { exitCode } = await $.process.run(['osascript', '-e', OPEN_HUB])

    return {
      text: exitCode === 0
        ? 'Quarterback opened in its own window.'
        : 'Could not open a Ghostty window. Run qb in any terminal.',
    }
  })

  on('turn.start', async ($, e, next) => {
    if (!e.agentId) {
      await update($, self, mine =>
        mine && {
          ...mine,
          status: 'working',
          activity: 'Thinking',
          prompt: e.text || mine.prompt,
        },
      )
    }

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (!e.agentId) {
      await update($, self, mine =>
        mine && { ...mine, status: 'complete', activity: 'Finished its turn' },
      )
    }

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const { agentId } = e
    const activity = describe(e)

    await update($, self, mine => {
      if (!mine) {
        return mine
      }

      return agentId
        ? {
            ...mine,
            agents: mine.agents.map(row =>
              row.id === agentId
                ? { ...row, activity, tools: row.tools + 1 }
                : row,
            ),
          }
        : { ...mine, activity }
    })

    return next(e)
  }).catch(($, e, next) => next(e))
}
