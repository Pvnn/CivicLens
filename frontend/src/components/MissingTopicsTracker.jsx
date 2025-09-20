import React, { useState, useEffect } from "react";
import WordCloud from "react-d3-cloud";
import { Bar } from "react-chartjs-2";
import axios from 'axios';

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

export default function MissingTopicsTracker() {
  const [chartData, setChartData] = useState(null);
  const [youthTopics, setYouthTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch data from the proxied API endpoint
        const response = await axios.get('/api/missing-topics');
        const data = response.data;
        
        // This assumes your Flask API returns data in a structure like:
        // [{ topic: "Climate", youth_mentions: 30, politician_mentions: 10 }]
        
        const allTopics = data.map(item => item.topic);
        
        setYouthTopics(data.map(item => ({
          text: item.topic,
          value: item.youth_mentions
        })));

        setChartData({
          labels: allTopics,
          datasets: [
            {
              label: "Youth Mentions",
              data: data.map(item => item.youth_mentions),
              backgroundColor: "rgba(75,192,192,0.6)",
            },
            {
              label: "Politician Mentions",
              data: data.map(item => item.politician_mentions),
              backgroundColor: "rgba(192,75,75,0.6)",
            },
          ],
        });
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data. Please check if the Flask backend is running.");
        setLoading(false);
      }
    };
    fetchData();
  }, []);

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

  const fontSizeMapper = word => Math.log2(word.value) * 5 + 16;
  const rotationDegrees = [-30, 0, 30, 60, 90];
  const rotate = () => rotationDegrees[Math.floor(Math.random() * rotationDegrees.length)];

  if (loading) {
    return <div className="p-4 bg-gray-800 rounded-lg text-white">Loading data...</div>;
  }

  if (error) {
    return <div className="p-4 bg-gray-800 rounded-lg text-red-400">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-2 text-white">Missing Topics Tracker</h2>

      <h3 className="font-semibold mb-2 text-white">Word Cloud (Youth Topics)</h3>
      <div className="h-64 mb-4">
        <WordCloud
          data={youthTopics}
          fontSizeMapper={fontSizeMapper}
          rotate={rotate}
          font="Impact"
          padding={5}
          fill="white"
        />
      </div>

      <h3 className="font-semibold mb-2 text-white">Topic Comparison</h3>
      <div className="h-64">
        {chartData ? (
          <Bar data={chartData} options={chartOptions} />
        ) : (
          <p className="text-white">No chart data available.</p>
        )}
      </div>
    </div>
  );
}