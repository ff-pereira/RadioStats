import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";

import Body from "../components/Body.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import InvalidData from "../components/InvalidData.jsx";
import StatsCharts from "../components/StatsCharts.jsx";
import {parseStatsData} from "../utils/StatsParser.jsx";
import StatsSummary from "../components/StatsSummary.jsx";

export default function RadioPage(){
    const api = useApi();
    const { radio_id } = useParams();

    const [radioStats, setRadioStats] = useState();
    const [chartData, setChartData] = useState({ categories: [], series: [] });

    useEffect(() => {
      (async () => {
        const response = await api.get(`/radio/stats/${radio_id}`);
        if (response.ok) {
          setRadioStats(response.body);
          setChartData(parseStatsData(response.body, undefined, true));
        }
      })();
    }, [api]);

    useEffect(() => {
      if (radioStats === undefined) return;
      document.title = radioStats === null ? "Radio - Not found" : `Radio - ${radioStats.name}`;
      return () => { document.title = "RadioStats"; };
    }, [radioStats]);

    return (
        <Body>
            <div className="h-[90vh] bg-primary/30 rounded-xl drop-shadow-2xl mt-[1.5vh] overflow-auto">
                {radioStats === undefined ?
                    <div className="h-[95%] w-full flex justify-center items-center">
                        <div className="spinner"></div>
                    </div>
                    :
                    <>
                        {radioStats === null ?
                            <InvalidData title="Radio"/>
                            :
                            <div className="md:grid md:grid-cols-2 md:grid-rows-3 md:gap-x-2 h-full min-h-0 relative">

                                <div className="relative grid grid-cols-3 gap-4 min-h-0">
                                    <div className="mx-6 my-4 flex justify-start items-center">
                                        <img src={radioStats.logo} alt="radio-logo" width={240} height={240} className="shadow-xl"/>
                                    </div>
                                    <div className="mt-4 md:mt-6 col-span-2 flex flex-col items-center">
                                        <div className="font-semibold text-3xl md:text-4xl border-b border-primary/50 pb-1">{radioStats.name}</div>
                                        <div className="mt-1 text-lg md:text-2xl">Radio</div>
                                    </div>
                                </div>

                                <div className="relative flex flex-col min-h-0 md:py-2 px-4">
                                    <div className="md:h-14 flex flex-col md:flex-row items-center justify-between mb-2 md:mx-16">
                                        <div className="md:text-xl">Since: <strong>{radioStats.first_day}</strong></div>
                                        <div className="md:text-xl">Last Update: <strong>{radioStats.last_day}</strong></div>
                                        <div className="md:text-xl">Total Days: <strong>{radioStats.total_days}</strong></div>
                                    </div>

                                    {radioStats && (
                                      <StatsSummary
                                        type="radio"
                                        stats={{
                                          total_plays: radioStats.total_plays,
                                          different_songs_count: radioStats.different_songs_count,
                                          avg_plays_per_song: radioStats.avg_plays_per_song,
                                        }}
                                        mostPlayed={radioStats.most_played}
                                      />
                                    )}
                                </div>

                                <div className="md:col-span-2 md:row-span-2 relative flex flex-col min-h-0 md:overflow-y-scroll mt-2 md:mt-0 pt-2 pb-4 px-4">
                                    {radioStats && <StatsCharts chartData={chartData}/>}
                                </div>
                            </div>
                        }
                    </>
                }
            </div>
        </Body>
    );
}
