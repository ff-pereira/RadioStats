import {useEffect, useState} from "react";
import Chart from "react-apexcharts";

export default function HourlyStackedChart({ series }) {
  const [isMd, setIsMd] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMd(window.innerWidth >= 768); // md breakpoint
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const height = isMd ? 350 : 500;
  const horizontal = !isMd;

  const options = {
    chart: {
      fontFamily: '"IBM Plex Sans", system-ui, sans-serif',
      type: "bar",
      stacked: true,
      height: height,
      toolbar: {
        show: false,
      },
      background: '#252121',
    },
    plotOptions: {
      bar: {
        horizontal: horizontal,
      },
    },
    xaxis: {
      categories: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
    },
    theme: {
      mode: "dark",
    },
    colors: [
      "#FFD13E", "#7C786B", "#FFB84C", "#A67C52", "#6C5B50",
      "#FF7F50", "#C0A16B", "#998877", "#FFDD7F", "#E38D00"
    ],
    title: {
      text: "Song Plays by Hour",
      align: "center",
      style: {
        fontSize: '16px',
        //fontWeight: 'bold',
        color: '#FFFFFF'
      }
    },
  };

  return (
    <div className="pt-2 px-2 bg-primary rounded-b-xl">
      <Chart options={options} series={series} type="bar" height={height} />
    </div>
  );
}
