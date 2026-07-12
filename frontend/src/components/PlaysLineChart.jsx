import Chart from "react-apexcharts";

export default function PlaysLineChart({ series }) {
  const chartData = {
    series,
    options: {
      chart: {
        fontFamily: '"IBM Plex Sans", system-ui, sans-serif',
        type: "line",
        height: 350,
        toolbar: {
          show: false,
        },
        zoom: {
          enabled: false,
        },
        background: '#252121',
      },
      xaxis: {
        type: "datetime",
      },
      colors: [
        "#FFD13E", "#7C786B", "#FFB84C", "#A67C52", "#6C5B50",
        "#FF7F50", "#C0A16B", "#998877", "#FFDD7F", "#E38D00"
      ],
      theme: {
        mode: "dark",
      },
      tooltip: {
        x: {
          formatter: (value) => {
            const date = new Date(value);
            const formatter = new Intl.DateTimeFormat("en-US", {
              weekday: "long",
              year: "numeric",
              month: "short",
              day: "numeric",
            });
            return formatter.format(date);
          },
        },
        y: {
          formatter: (value) => value === 0 ? undefined : value
        }
      },
      title: {
        text: "Song Plays by Day",
        align: "center",
        style: {
          fontSize: '16px',
          //fontWeight: 'bold',
          color: '#FFFFFF'
        }
      },
      // markers: {
      //   size: 3,
      // }
    },
  };

  return (
    <div className="pt-2 px-2 bg-primary rounded-t-xl">
      <Chart options={chartData.options} series={chartData.series} type="line" height={350}/>
    </div>
  );
}
