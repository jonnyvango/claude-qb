#!/usr/bin/env node
// The standalone hub: a full-window board, with no Claude Code session around it.
import { spawnSync } from 'node:child_process'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

import {
  combine,
  FORGET_MS,
  jumpable,
  latestTitle,
  parseJson,
  renderHub,
} from '../hooks/board.ts'
import type { RegistryEntry, SessionRow } from '../types'

const REFRESH_MS = 2000
const ROOT = join(homedir(), '.claude')
const PUBLISHED = join(ROOT, 'quarterback')
const REGISTRY = join(ROOT, 'sessions')
const TRANSCRIPTS = join(ROOT, 'projects')

// Takes the tty as an argument, so nothing from a session file enters the script.
const FOCUS_TAB = `on run argv
  tell application "Ghostty"
    repeat with t in terminals
      if (tty of t) is (item 1 of argv) then
        focus t
        activate
        return
      end if
    end repeat
  end tell
  error "no such tab"
end run`

// Only the .json files: the .key files beside the registry's are secrets.
const readJsonDir = <T,>(dir: string) => {
  try {
    return readdirSync(dir)
      .filter(name => name.endsWith('.json'))
      .flatMap(name => {
        try {
          return parseJson<T>(readFileSync(join(dir, name), 'utf8')) ?? []
        } catch {
          // The session left between listing and reading.
          return []
        }
      })
  } catch {
    return []
  }
}

// A crashed session leaves its file behind; ps says which pids are real.
const liveTtys = (registry: RegistryEntry[]) => {
  const pids = registry.map(entry => entry.pid).join(',')

  if (pids === '') {
    return new Map<number, string>()
  }

  const { stdout } = spawnSync('ps', ['-o', 'pid=,tty=', '-p', pids], {
    encoding: 'utf8',
  })

  return new Map(
    stdout
      .split('\n')
      .filter(line => line.trim() !== '')
      .map(line => line.trim().split(/\s+/))
      .map(([pid, tty]) => [Number(pid), tty ?? ''] as const),
  )
}

const load = (now: number) => {
  const published = readJsonDir<SessionRow>(PUBLISHED).filter(
    row => now - row.beatAt <= FORGET_MS,
  )
  const registry = readJsonDir<RegistryEntry>(REGISTRY)
  const ttys = liveTtys(registry)

  return combine(
    published,
    registry.filter(entry => ttys.has(entry.pid)),
    now,
    ttys,
  )
}

const transcriptOf = (id: string) => {
  for (const dir of readdirSync(TRANSCRIPTS)) {
    const path = join(TRANSCRIPTS, dir, `${id}.jsonl`)

    try {
      return { path, modified: statSync(path).mtimeMs }
    } catch {
      // Not this project's session; try the next.
    }
  }

  return undefined
}

const titles = new Map<string, string>()
const checked = new Map<string, number>()

// Transcripts grow large, so one is read again only after it changed.
const refreshTitles = (rows: SessionRow[]) => {
  for (const { id } of rows) {
    const found = transcriptOf(id)

    if (found && checked.get(id) !== found.modified) {
      checked.set(id, found.modified)
      const title = latestTitle(readFileSync(found.path, 'utf8'))

      if (title) {
        titles.set(id, title)
      }
    }
  }
}

let rows: SessionRow[] = []

const draw = () => {
  const lines = renderHub(rows, titles, Date.now(), {
    columns: process.stdout.columns,
    height: process.stdout.rows,
  })

  process.stdout.write(`\x1b[H${lines.join('\x1b[K\n')}\x1b[K\x1b[J`)
}

const refresh = () => {
  rows = load(Date.now())
  refreshTitles(rows)
  draw()
}

const leave = () => {
  // Line wrap, the cursor and the main screen, as they were.
  process.stdout.write('\x1b[?7h\x1b[?25h\x1b[?1049l')
  process.exit(0)
}

// A pipe has no window to take over.
if (!process.stdout.isTTY || !process.stdin.isTTY) {
  console.error('qb needs a terminal.')
  process.exit(1)
}

process.title = 'qb'
process.stdout.write('\x1b]2;Quarterback\x07\x1b[?1049h\x1b[?25l\x1b[?7l')
process.stdin.setRawMode(true)
process.stdin.setEncoding('utf8')
process.stdin.on('data', (key: string) => {
  if (key === 'q' || key === '\x03') {
    leave()
  }

  const target = jumpable(rows)[Number(key) - 1]

  if (target) {
    spawnSync('osascript', ['-e', FOCUS_TAB, `/dev/${target.tty}`])
  }
})
process.stdout.on('resize', draw)
process.on('SIGTERM', leave)
process.on('SIGHUP', leave)

refresh()
setInterval(refresh, REFRESH_MS)
