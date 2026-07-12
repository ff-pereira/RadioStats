import Chart from "react-apexcharts";

export default function WeekdayStackedChart({ series }) {
  const options = {
    chart: {
      fontFamily: '"IBM Plex Sans", system-ui, sans-serif',
      type: "bar",
      stacked: true,
      height: 350,
      toolbar: {
        show: false,
      },
      background: '#252121',
    },
    plotOptions: {
      bar: {
        horizontal: true,
      },
    },
    xaxis: {
      categories: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    },
    colors: [
      "#FFD13E", "#7C786B", "#FFB84C", "#A67C52", "#6C5B50",
      "#FF7F50", "#C0A16B", "#998877", "#FFDD7F", "#E38D00"
    ],
    theme: {
      mode: "dark",
    },
    title: {
      text: "Song Plays by Weekday",
      align: "center",
      style: {
        fontSize: '16px',
        //fontWeight: 'bold',
        color: '#FFFFFF'
      }
    },
  };

  return (
    <div className="pt-2 px-2 bg-primary">
      <Chart options={options} series={series} type="bar" height={350} />
    </div>
  );
}
