"use client";

import { useState } from "react";

import StrategyChart from "../components/StrategyChart";

type StrategyPerformance = {
  name: string;
  expected_annualized_return: number;
  max_drawdown: number;
  suggested_direction: "long" | "short" | "neutral";
  confidence_score: number;
};

type AssetRecommendation = {
  asset: string;
  detected_regime: string;
  top_strategies: StrategyPerformance[];
};

export default function Home() {
  const [data, setData] = useState<AssetRecommendation[]>([]);
  const [loading, setLoading] = useState(false);

  const runAnalysis = async () => {
    setLoading(true);
    const res = await fetch("http://localhost:8000/api/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assets: ["BTCUSDT", "ETHUSDT"],
        market: "crypto",
        timeframe: "1h",
        lookback_bars: 500,
      }),
    });
    const json = await res.json();
    setData(json);
    setLoading(false);
  };

  return (
    <main style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>Trading Research & Strategy Automation</h1>
      <button onClick={runAnalysis} disabled={loading}>
        {loading ? "Running..." : "Analyze Market"}
      </button>

      {data.map((asset) => (
        <section key={asset.asset} style={{ marginTop: 24 }}>
          <h2>{asset.asset}</h2>
          <p>Current detected regime: {asset.detected_regime}</p>
          <StrategyChart strategies={asset.top_strategies} />
          <table style={{ width: "100%", marginTop: 12 }}>
            <thead>
              <tr>
                <th>Strategy</th>
                <th>Expected annualized return</th>
                <th>Max drawdown</th>
                <th>Direction</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {asset.top_strategies.map((s) => (
                <tr key={s.name}>
                  <td>{s.name}</td>
                  <td>{(s.expected_annualized_return * 100).toFixed(2)}%</td>
                  <td>{(s.max_drawdown * 100).toFixed(2)}%</td>
                  <td>{s.suggested_direction}</td>
                  <td>{s.confidence_score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </main>
  );
}
