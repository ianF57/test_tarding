const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess;

function getPythonCommand() {
  if (process.platform === 'win32') return 'python';
  return 'python3';
}

function startBackend() {
  const backendRoot = path.resolve(__dirname, '..', 'backend');
  const python = getPythonCommand();

  backendProcess = spawn(
    python,
    ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
    { cwd: backendRoot, stdio: 'inherit' }
  );

  backendProcess.on('exit', (code) => {
    console.log('Backend exited with code', code);
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1320,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});
