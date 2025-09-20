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
        const response = await axios.get('/api/missing-topics');
        const data = response.data;
        
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
        labels: {
          color: 'white',
        }
      },
      title: {
        display: true,
        text: 'Youth vs. Politician Topic Mentions',
        color: 'white'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: 'white'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        ticks: {
          color: 'white'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
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
    <div className="p-6 bg-gray-800 rounded-xl shadow-lg border border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-white">Missing Topics Tracker</h2>
      
      {/* Grid Layout for a more professional look */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Word Cloud Card */}
        <div className="bg-gray-900 rounded-lg p-4 shadow-inner border border-gray-700">
          <h3 className="text-lg font-semibold mb-2 text-white">Top Youth Concerns (Word Cloud)</h3>
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
        </div>

        {/* Bar Chart Card */}
        <div className="bg-gray-900 rounded-lg p-4 shadow-inner border border-gray-700">
          <h3 className="text-lg font-semibold mb-2 text-white">Topic Comparison (Bar Chart)</h3>
          <div className="h-64">
            {chartData ? (
              <Bar data={chartData} options={chartOptions} />
            ) : (
              <p className="text-gray-400">No chart data available.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}