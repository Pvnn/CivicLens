import React from "react";
import WordCloud from "react-d3-cloud";
import { Bar } from "react-chartjs-2";

// Import and register Chart.js components
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Mock data
const youthTopics = [
  { text: "Climate", value: 30 },
  { text: "Jobs", value: 25 },
  { text: "Transport", value: 20 },
  { text: "Education", value: 18 },
  { text: "Mental Health", value: 15 },
  { text: "Housing", value: 12 },
  { text: "Equality", value: 10 },
  { text: "Environment", value: 8 },
];

const politicianTopics = ["Economy", "Jobs", "Defense", "Infrastructure"];

export default function MissingTopicsTracker() {
  const allTopics = Array.from(
    new Set([...youthTopics.map(t => t.text), ...politicianTopics])
  );

  const chartData = {
    labels: allTopics,
    datasets: [
      {
        label: "Youth Mentions",
        data: allTopics.map(t => youthTopics.find(y => y.text === t)?.value || 0),
        backgroundColor: "rgba(75,192,192,0.6)",
      },
      {
        label: "Politician Mentions",
        data: allTopics.map(t => (politicianTopics.includes(t) ? 20 : 0)),
        backgroundColor: "rgba(192,75,75,0.6)",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Youth vs. Politician Topic Mentions',
      },
    },
  };

  // Improved fontSizeMapper for better word cloud visibility
  const fontSizeMapper = word => Math.log2(word.value) * 5 + 16;
  
  // Custom rotation for better visual appeal
  const rotationDegrees = [-30, 0, 30, 60, 90];
  const rotate = () => rotationDegrees[Math.floor(Math.random() * rotationDegrees.length)];

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-2 text-white">Missing Topics Tracker</h2>

      <h3 className="font-semibold mb-2 text-white">Word Cloud (Youth Topics)</h3>
      <div className="h-64 mb-4">
        <WordCloud
          data={youthTopics}
          fontSizeMapper={fontSizeMapper}
          rotate={rotate}
          font="Impact" // You can change this to any font you like
          padding={5}
          fill="white" // Ensure text is visible on dark background
        />
      </div>

      <h3 className="font-semibold mb-2 text-white">Topic Comparison</h3>
      <div className="h-64">
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}