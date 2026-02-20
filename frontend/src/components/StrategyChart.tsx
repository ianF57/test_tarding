"use client";

import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

type Strategy = {
  name: string;
  expected_annualized_return: number;
  confidence_score: number;
};

export default function StrategyChart({ strategies }: { strategies: Strategy[] }) {
  const data = {
    labels: strategies.map((s) => s.name),
    datasets: [
      {
        label: "Expected Annualized Return",
        data: strategies.map((s) => Number((s.expected_annualized_return * 100).toFixed(2))),
        backgroundColor: "rgba(53, 162, 235, 0.5)",
      },
      {
        label: "Confidence Score",
        data: strategies.map((s) => Number(s.confidence_score.toFixed(2))),
        backgroundColor: "rgba(255, 99, 132, 0.5)",
      },
    ],
  };

  return <Bar data={data} />;
}
