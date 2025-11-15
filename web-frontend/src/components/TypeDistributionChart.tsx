import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip);

interface Props {
  data: Record<string, number>;
}

const TypeDistributionChart = ({ data }: Props) => {
  const labels = Object.keys(data);
  const counts = Object.values(data);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Equipment count",
        data: counts,
        backgroundColor: "rgba(67, 56, 202, 0.7)",
      },
    ],
  };

  return (
    <figure aria-label="Chart displaying equipment distribution by type">
      <Bar
        aria-description="Histogram showing the count of each equipment type"
        role="img"
        data={chartData}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            x: {
              ticks: { color: "#1f2937" },
            },
            y: {
              ticks: { color: "#1f2937" },
            },
          },
        }}
        style={{ height: "240px", minHeight: "240px", width: "100%" }}
      />
      <figcaption className="sr-only">Equipment distribution chart</figcaption>
    </figure>
  );
};

export default TypeDistributionChart;
