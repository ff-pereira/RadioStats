import PlaysLineChart from "./PlaysLineChart.jsx";
import WeekdayStackedChart from "./WeekdayStackedChart.jsx";
import TimeOfDayPieChart from "./TimeOfDayPieChart.jsx";
import HourlyStackedChart from "./HourlyStackedChart.jsx";

export default function StatsCharts({ chartData }) {
    return (
        <div className="md:grid md:grid-cols-4">
            <div className="md:col-span-full">
                <PlaysLineChart categories={chartData.categories}
                                series={chartData.series}/>
            </div>
            <div className="md:col-span-3">
                <WeekdayStackedChart series={chartData.weekdaySeries}/>
            </div>

            <div className="md:col-span-1">
                <TimeOfDayPieChart series={chartData.timeOfDaySeries}/>
            </div>

            <div className="md:col-span-full">
                <HourlyStackedChart series={chartData.hourlySeries}/>
            </div>
        </div>
    );
}