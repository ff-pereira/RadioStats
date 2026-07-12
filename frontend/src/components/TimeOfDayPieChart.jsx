import Chart from "react-apexcharts";

export default function TimeOfDayPieChart({ series }) {
  const options = {
    chart: {
      fontFamily: '"IBM Plex Sans", system-ui, sans-serif',
      type: "pie",
      height: 350,
      background: '#252121',
    },
    labels: ["dawn", "morning", "afternoon", "night"],
    dataLabels: {
      enabled: true,
      dropShadow: {
        enabled: false,
      },
      formatter: function (val, opts) {
        const count = opts.w.globals.series[opts.seriesIndex];
        const label = opts.w.globals.labels[opts.seriesIndex];
        return [`${label}`,`${count}`, `${val.toFixed(1)}%`];
      },
    },
    plotOptions: {
      pie: {
        dataLabels: {
          offset: -30,
        },
        expandOnClick: false,
      }
    },
    tooltip: {
      enabled: false,
      fillSeriesColor: false,
    },
    colors: [
      "#FFD13E", "#7C786B", "#FFB84C", "#A67C52", "#6C5B50",
      "#FF7F50", "#C0A16B", "#998877", "#FFDD7F", "#E38D00"
    ],
    theme: {
      mode: "dark",
    },
    title: {
      text: "Song Plays by Time of Day",
      align: "left",
      style: {
        fontSize: '16px',
        //fontWeight: 'bold',
        color: '#FFFFFF'
      }
    },
    legend: {
        show: false,
    }
  };

  return (
    <div className="pt-2 px-2 bg-primary h-full">
      <Chart options={options} series={series} type="pie" height={350}/>
    </div>
  );
}