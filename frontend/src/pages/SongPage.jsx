import { useState, useEffect } from 'react';
import {Link, useParams} from "react-router-dom";

import Body from "../components/Body.jsx";
import Album from "../components/Album.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import InvalidData from "../components/InvalidData.jsx";
import StatsCharts from "../components/StatsCharts.jsx";
import {parseStatsData} from "../utils/StatsParser.jsx";
import StatsSummary from "../components/StatsSummary.jsx";
import RadioSelector from "../components/RadioSelector.jsx";

export default function SongPage(){
    const api = useApi();
    const { song_id } = useParams();

    const [song, setSong] = useState();
    const [songStats, setSongStats] = useState();
    const [songRanking, setSongRanking] = useState();
    const [radioNames, setRadioNames] = useState({});
    const [activeAlbumId, setActiveAlbumId] = useState(null);
    const [selectedRadios, setSelectedRadios] = useState([]);
    const [chartData, setChartData] = useState({ categories: [], series: [] });

    const [isMd, setIsMd] = useState(false);

    useEffect(() => {
        (async () => {
            const response = await api.get(`/radios/song/${song_id}`);
            if (response.ok) {
            setRadioNames(response.body.radio_names || {});
            }
        })();
    }, [api]);

    useEffect(() => {
            (async () => {
                const response = await api.get('/song/' + song_id);
                setSong(response.ok ? response.body : null);
                console.log(response.body);
            })();
        }, [api]);

    useEffect(() => {
      (async () => {
        if (Object.keys(radioNames).length === 1) return;

        const radiosParam = selectedRadios.length > 0 ? `?radios=${selectedRadios.join(",")}` : "";
        const response = await api.get(`/song/stats/${song_id}${radiosParam}`);

        if (response.ok) {
          setSongStats(response.body);
          setChartData(parseStatsData(response.body, "radio_names"));
        }
      })();
    }, [api, selectedRadios]);

    useEffect(() => {
      (async () => {
        if (Object.keys(radioNames).length === 1) return;

        const radiosParam = selectedRadios.length > 0 ? `?radios=${selectedRadios.join(",")}` : "";
        const response = await api.get(`/song/ranking/${song_id}${radiosParam}`);

        if (response.ok) {
          setSongRanking(response.body);
        }
      })();
    }, [api, selectedRadios]);

    useEffect(() => {
        const handleResize = () => setIsMd(window.innerWidth >= 768);
        handleResize();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    useEffect(() => {
      if (song === undefined) return;
      document.title = song === null ? "Song - Not found" : `Song - ${song.name}`;
      return () => { document.title = "RadioStats"; };
    }, [song]);

    return (
        <Body>
            <div className="h-[90vh] bg-primary/30 rounded-xl drop-shadow-2xl mt-[1.5vh] overflow-auto">

                {song === undefined ?
                    <div className="h-[95%] w-full flex justify-center items-center">
                        <div className="spinner"></div>
                    </div>
                    :
                    <>
                        {song === null ?
                            <InvalidData title="Song"/>
                            :
                            <div className="md:grid md:grid-cols-2 md:grid-rows-3 md:gap-x-2 h-full min-h-0 relative">
                                <div className="relative grid grid-cols-3 gap-4 min-h-0">
                                    <div className="mx-6 my-4 flex justify-start items-center aspect-square">
                                        <Album
                                            id={song.album_id}
                                            imageUrl={song.album_cover_url}
                                            size={isMd ? "normal" : "very-small"}
                                            audioUrl={song.sample}
                                            activeAlbumId={activeAlbumId}
                                            setActiveAlbumId={setActiveAlbumId}
                                        />
                                    </div>
                                    <div className="mt-4 md:mt-6 col-span-2 flex flex-col items-center mr-4 md:mr-0 text-center relative">
                                        <div className={`font-semibold border-b border-primary/50 pb-1 md:text-4xl ${
                                            song.name.length > 12 ? "text-2xl" : "text-3xl"}`}>
                                            {song.name}
                                        </div>
                                        <div className="mt-1 text-lg md:text-2xl hover:scale-105 ease-in-out duration-200">
                                            <Link to={`/artist/${song.lead_artist_id}`}>{song.lead_artist_name}</Link>
                                        </div>

                                        <div className="my-2 flex flex-col items-center md:items-start md:flex-row md:flex-wrap md:gap-2">
                                          {song.other_artists.map((artist, index) => (
                                            <div
                                              key={artist.id}
                                              className="text-base md:text-lg hover:scale-105 ease-in-out duration-200 flex items-center"
                                            >
                                              <Link to={`/artist/${artist.id}`}>{artist.name}</Link>
                                              {index < song.other_artists.length - 1 && (
                                                <span className="hidden md:inline">,&nbsp;</span>
                                              )}
                                            </div>
                                          ))}
                                        </div>


                                        {songRanking && isMd &&
                                            <div className="grid grid-cols-2 mt-4 absolute bottom-6">
                                                <div
                                                    className="flex flex-col justify-center items-center border-r border-primary/50 pr-2 mr-2">
                                                    <div className="font-semibold text-lg">Rank</div>
                                                    <div className="text-2xl">{songRanking.rank}</div>
                                                </div>
                                                <div
                                                    className="flex flex-col justify-center items-center pl-2 ml-2">
                                                    <div className="font-semibold text-lg">Percentile</div>
                                                    <div className="text-2xl">{songRanking.percentile}%</div>
                                                </div>
                                            </div>
                                        }
                                    </div>
                                </div>

                                <div className="relative flex flex-col min-h-0 py-2 px-4">
                                    <div className="h-14 flex items-center justify-center mb-2">
                                        <RadioSelector
                                            radios={Object.entries(radioNames).map(([id, logo]) => ({id, logo}))}
                                            selected={selectedRadios}
                                            setSelected={setSelectedRadios}
                                        />
                                    </div>

                                    {songStats && (
                                      <StatsSummary
                                        type="song"
                                        stats={{
                                          total_plays: songStats.total_plays,
                                          different_radios_count: songStats.different_radios_count,
                                        }}
                                        mostPlayed={songStats.most_played}
                                        countsByRadio={songStats.play_counts_by_radio}
                                      />
                                    )}

                                    {songRanking && !isMd &&
                                    <div className="grid grid-cols-2 mt-4 mb-2">
                                        <div
                                            className="flex flex-col justify-center items-center border-r border-primary/50 pr-2 mr-2">
                                            <div className="font-semibold text-base">Rank</div>
                                            <div className="text-xl">{songRanking.rank}</div>
                                        </div>
                                        <div
                                            className="flex flex-col justify-center items-center pl-2 ml-2">
                                            <div className="font-semibold text-base">Percentile</div>
                                            <div className="text-xl">{songRanking.percentile}%</div>
                                        </div>
                                    </div>
                                    }
                                </div>

                                <div
                                    className="col-span-2 row-span-2 relative flex flex-col min-h-0 overflow-y-scroll pt-2 pb-4 px-4">
                                    {songStats && <StatsCharts chartData={chartData}/>}
                                </div>
                            </div>
                        }
                    </>
                }
            </div>
        </Body>
    );
}
