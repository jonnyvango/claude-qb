import { combine, description, jumpable, latestTitle, renderHub } from './board'
import { expect, test } from 'claude-code/testing'

const session = {
  id: 's1',
  project: 'shop',
  prompt: 'Fix checkout',
  status: 'working',
  activity: 'Bash: npm test',
  beatAt: 0,
  agents: [{
    id: 'a1',
    label: 'Find bug',
    type: 'Explore',
    status: 'running',
    activity: 'Read: /x.ts',
    tools: 3,
  }],
}

const entry = {
  pid: 1,
  sessionId: 's2',
  cwd: '/code/blog',
  name: 'blog-a1',
  status: 'idle',
}

const room = { columns: 80, height: 40 }

test('an open session without the plugin still gets a row', () => {
  const [row] = combine([], [{ ...entry, status: 'busy' }], 1000)

  expect(row?.project).toBe('blog')
  expect(row?.status).toBe('working')
})

test('what a session published beats the registry', () => {
  const published = { ...session, id: 's2', beatAt: 1000 }
  const rows = combine([published], [entry], 1000)

  expect(rows.length).toBe(1)
  expect(rows[0]?.status).toBe('working')
})

test('a parked session reads idle though the registry says busy', () => {
  const [row] = combine([], [{ ...entry, status: 'busy', parkedJobId: 'j' }], 1000)

  expect(row?.status).toBe('idle')
})

test('a row carries the tty of its session', () => {
  const ttys = new Map([[1, 'ttys012']])
  const [row] = combine([], [entry], 1000, ttys)

  expect(row?.tty).toBe('ttys012')
})

test('the newest title in a transcript wins', () => {
  const transcript = [
    '{"type":"ai-title","aiTitle":"Old","sessionId":"s1"}',
    '{"type":"user","text":"{\\"type\\":\\"ai-title\\",\\"aiTitle\\":\\"Quoted\\"}"}',
    '{"type":"ai-title","aiTitle":"New","sessionId":"s1"}',
    '{"type":"assistant"}',
  ].join('\n')

  expect(latestTitle(transcript)).toBe('New')
  expect(latestTitle('{"type":"user"}')).toBe(undefined)
})

test('a resumed title gives way, and the person\'s own title beats all', () => {
  const resumed = '{"type":"ai-title","aiTitle":"Resuming previous session"}'
  const named = '{"type":"custom-title","customTitle":"Mine"}'

  expect(latestTitle(resumed)).toBe(undefined)
  expect(latestTitle(`{"type":"ai-title","aiTitle":"Real"}\n${resumed}`)).toBe('Real')
  expect(latestTitle(`${named}\n{"type":"ai-title","aiTitle":"Real"}`)).toBe('Mine')
})

test('a session is described by its title, else its prompt, else nothing yet', () => {
  expect(description(session, 'Checkout fix')).toBe('Checkout fix')
  expect(description({ ...session, prompt: 'One\ntwo' })).toBe('One')
  expect(description({ ...session, prompt: '' })).toBe('No prompt yet')
})

test('sessions in a project share one section', () => {
  const rows = [
    session,
    { ...session, id: 's3', prompt: 'Add tax' },
    { ...session, id: 's4', project: 'blog', prompt: 'New post' },
  ]
  const lines = renderHub(rows, new Map([['s1', 'Checkout fix']]), 0, room).join('\n')

  expect(lines.split('shop').length - 1).toBe(1)
  expect(lines.split('blog').length - 1).toBe(1)
  expect(lines).toContain('Checkout fix')
  expect(lines).toContain('Add tax')
  expect(lines).toContain('Find bug: Read: /x.ts (3 tool calls)')
})

test('only sessions in a real tab take a digit, in board order', () => {
  const rows = [
    session,
    { ...session, id: 's3', tty: 'ttys012' },
    { ...session, id: 's4', tty: '??' },
  ]

  expect(jumpable(rows).map(row => row.id)).toEqual(['s3'])
})

test('a board too tall for the window says what it left out', () => {
  const lines = renderHub([session], new Map(), 0, { columns: 80, height: 6 })

  expect(lines.length).toBe(6)
  expect(lines.join('\n')).toContain('more lines')
})
