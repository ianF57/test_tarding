const apiBase = window.appInfo.apiBase;

async function loadSettings() {
  const res = await fetch(`${apiBase}/settings`);
  const s = await res.json();
  document.getElementById('binanceApiKey').value = s.binance_api_key || '';
  document.getElementById('oandaApiKey').value = s.oanda_api_key || '';
  document.getElementById('cmeApiKey').value = s.cme_api_key || '';
  document.getElementById('defaultMarket').value = s.default_market || 'crypto';
  document.getElementById('defaultTimeframe').value = s.default_timeframe || '1h';
  document.getElementById('defaultAssets').value = (s.default_assets || ['BTCUSDT']).join(',');
}

async function saveSettings() {
  const payload = {
    binance_api_key: document.getElementById('binanceApiKey').value,
    oanda_api_key: document.getElementById('oandaApiKey').value,
    cme_api_key: document.getElementById('cmeApiKey').value,
    default_market: document.getElementById('defaultMarket').value,
    default_timeframe: document.getElementById('defaultTimeframe').value,
    default_assets: document.getElementById('defaultAssets').value.split(',').map((v) => v.trim()).filter(Boolean)
  };

  const res = await fetch(`${apiBase}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  document.getElementById('settingsStatus').textContent = res.ok
    ? 'Settings saved.'
    : 'Failed to save settings.';
}

function renderTables(data) {
  const node = document.getElementById('tables');
  node.innerHTML = '';
  data.forEach((assetBlock) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<h3>${assetBlock.asset}</h3><p>Regime: ${assetBlock.detected_regime}</p>`;

    const table = document.createElement('table');
    table.innerHTML = `
      <thead><tr>
        <th>Strategy</th><th>Expected Annual Return</th><th>Max DD</th><th>Direction</th><th>Confidence</th>
      </tr></thead>
      <tbody>
        ${assetBlock.top_strategies.map((s) => `
          <tr>
            <td>${s.name}</td>
            <td>${(s.expected_annualized_return * 100).toFixed(2)}%</td>
            <td>${(s.max_drawdown * 100).toFixed(2)}%</td>
            <td>${s.suggested_direction}</td>
            <td>${s.confidence_score.toFixed(1)}</td>
          </tr>`).join('')}
      </tbody>`;

    card.appendChild(table);
    node.appendChild(card);
  });
}

async function analyze() {
  const assets = document.getElementById('defaultAssets').value.split(',').map((v) => v.trim()).filter(Boolean);
  const payload = {
    assets,
    market: document.getElementById('defaultMarket').value,
    timeframe: document.getElementById('defaultTimeframe').value,
    lookback_bars: 500
  };

  document.getElementById('output').textContent = 'Running analysis...';
  const res = await fetch(`${apiBase}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  document.getElementById('output').textContent = JSON.stringify(data, null, 2);
  if (Array.isArray(data)) renderTables(data);
}

document.getElementById('saveSettings').addEventListener('click', saveSettings);
document.getElementById('analyzeBtn').addEventListener('click', analyze);

loadSettings().catch((e) => {
  document.getElementById('output').textContent = `Startup error: ${e}`;
});
