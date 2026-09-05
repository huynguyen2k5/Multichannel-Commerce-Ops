import { spawn } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')
const backendDir = path.join(rootDir, 'backend')

const isWin = process.platform === 'win32'
const venvPython = isWin
  ? path.join(backendDir, '.venv', 'Scripts', 'python.exe')
  : path.join(backendDir, '.venv', 'bin', 'python')

const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python'

const child = spawn(pythonCmd, ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'], {
  cwd: backendDir,
  stdio: 'inherit',
  shell: false,
})

child.on('error', (err) => {
  console.error('[backend] Failed to start uvicorn:', err)
})

child.on('exit', (code) => {
  process.exit(code ?? 0)
})
