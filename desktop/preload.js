const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('appInfo', {
  name: 'Trading Research Desktop',
  apiBase: 'http://127.0.0.1:8000/api'
});
