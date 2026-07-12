import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import Body from "../components/Body.jsx";
import Song from "../components/Song.jsx";
import { useApi } from "../contexts/ApiProvider";
import InvalidData from "../components/InvalidData.jsx";
import StatsCharts from "../components/StatsCharts.jsx";
import {parseStatsData} from "../utils/StatsParser.jsx";
import StatsSummary from "../components/StatsSummary.jsx";
import RadioSelector from "../components/RadioSelector.jsx";

export default function ArtistPage() {
  const api = useApi();
  const { artist_id } = useParams();

  const [artist, setArtist] = useState();
  const [chartData, setChartData] = useState({});
  const [artistStats, setArtistStats] = useState(null);
  const [radioNames, setRadioNames] = useState({});
  const [viewMode, setViewMode] = useState("lead");
  const [artistRanking, setArtistRanking] = useState(null);
  const [activeAlbumId, setActiveAlbumId] = useState(null);
  const [selectedRadios, setSelectedRadios] = useState([]);

  const leadParam = viewMode === "lead" ? "1" : "0";

  useEffect(() => {
    (async () => {
      const response = await api.get(`/radios/artist/${artist_id}?lead=${viewMode === "lead" ? "1" : "0"}`);
      if (response.ok) {
        setRadioNames(response.body.radio_names || {});
      }
    })();
  }, [leadParam]);

  useEffect(() => {
    (async () => {
      const response = await api.get(`/artist/${artist_id}`);
      setArtist(response.ok ? response.body : null);

      if(response.ok && response.body){
        const a = response.body;
        if (a.songs.length === 0 && a.songs_as_other.length > 0) {
            setViewMode("other");
        }
      }

    })();
  }, [api]);

  useEffect(() => {
    (async () => {
      if (Object.keys(radioNames).length === 1) return;

      const radiosParam = selectedRadios.length > 0 ? `&radios=${selectedRadios.join(",")}` : "";
      const leadParam = viewMode === "lead" ? "1" : "0";
      const response = await api.get(`/artist/stats/${artist_id}?lead=${leadParam}${radiosParam}`);

      if (response.ok) {
        setArtistStats(response.body);
        setChartData(parseStatsData(response.body, "song_names"));
      }
    })();
  }, [api, viewMode, selectedRadios]);

  useEffect(() => {
    (async () => {
      if (Object.keys(radioNames).length === 1) return;

      const radiosParam = selectedRadios.length > 0 ? `&radios=${selectedRadios.join(",")}` : "";
      const leadParam = viewMode === "lead" ? "1" : "0";
      const response = await api.get(`/artist/ranking/${artist_id}?lead=${leadParam}${radiosParam}`);

      if (response.ok) {
        setArtistRanking(response.body);
      } else{
        setArtistRanking(null);
      }
    })();
  }, [api, viewMode, selectedRadios]);

  useEffect(() => {
    setSelectedRadios([]);
    setRadioNames({});
  }, [viewMode]);

  useEffect(() => {
    if (artist === undefined) return;
    document.title = artist === null ? "Artist - Not found" : `Artist - ${artist.name}`;
    return () => { document.title = "RadioStats"; };
  }, [artist]);

  return (
    <Body>
      <div className="h-[90vh] bg-primary/30 rounded-xl drop-shadow-2xl mt-[1.5vh] overflow-auto">

        {artist === undefined ?
            <div className="h-[95%] w-full flex justify-center items-center">
              <div className="spinner"></div>
            </div>
            :
            <>
              {artist === null ?
                <InvalidData title="Artist"/>
                :
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:h-full relative">

                    <div className="md:h-full relative flex flex-col min-h-0">
                      <div className="md:h-1/3 overflow-hidden p-4 relative">
                        <div className="grid grid-cols-7 gap-4">
                          <div className="col-span-4 flex flex-col">
                            <div className={`font-bold ${artist.name.length > 12 ? "text-3xl md:text-4xl" : "text-4xl md:text-5xl"}`}>
                              {artist.name}
                            </div>
                            {artist.artist_type && <div className="text-lg">{artist.artist_type[0].toUpperCase() + artist.artist_type.slice(1)}</div>}
                          </div>
                          {artistRanking &&
                              <>
                                <div className={`${artist.flag ? "col-span-2" : "col-span-3"} grid md:grid-cols-2 pb-4 md:pb-2 px-2`}>
                                    <div className="flex flex-col justify-start items-center md:border-r md:border-primary/50 md:pr-2 md:mr-2">
                                        <div className="font-semibold text-sm md:text-lg">Rank</div>
                                        <div className="text-sm md:text-xl">{artistRanking.rank}</div>
                                    </div>
                                    <div className="flex flex-col justify-start items-center md:pl-2 md:ml-2">
                                        <div className="font-semibold text-sm md:text-lg">Percentile</div>
                                        <div className="text-sm md:text-xl">{artistRanking.percentile}%</div>
                                    </div>
                                </div>
                                {artist.flag &&
                                  <div className="flex flex-col justify-start items-end">
                                    <img className="w-12 md:w-18 rounded-md"
                                         src={artist.flag} alt="Flag"/>
                                  </div>
                                }
                              </>
                          }
                        </div>

                        <div className="hidden md:block my-2 h-2/3 overflow-y-auto text-black font-medium">
                          {artist.description || "No description available for this artist."}
                        </div>
                        <div className="hidden md:block absolute bottom-0 left-4 text-sm">
                          Artist's descriptions are automatically generated by artificial intelligence and may contain inaccuracies.
                        </div>
                        <div className="absolute bottom-0 right-4">Average per song: <strong>{artistStats?.avg_plays_per_song || 0}</strong></div>
                      </div>

                      <div className="md:h-2/3 overflow-y-auto min-h-0 pt-2 px-4 pb-4">
                        {artistStats && (
                            <div className="px-3 md:px-0 py-4 h-52 md:h-full overflow-x-auto md:overflow-x-hidden overflow-y-hidden md:overflow-y-auto with-scrollbar bg-accent/40 rounded-xl flex md:grid flex-nowrap md:grid-cols-2 xl:grid-cols-4 gap-4">
                              { artistStats.play_counts_by_song?.map((song) => (
                                <Song
                                  song={song}
                                  key={song.id}
                                  albumSize="small"
                                  activeAlbumId={activeAlbumId}
                                  setActiveAlbumId={setActiveAlbumId}
                                  playCount={song.play_count}
                                />
                              ))}
                          </div>
                        )}
                      </div>

                    </div>

                    <div className="md:h-full relative flex flex-col min-h-0">

                      <div className="md:h-1/3 md:overflow-auto py-2 px-4">

                        <div className="-mt-3 md:mt-0 h-14 flex items-center justify-center mb-2">
                          <div className="flex items-center">
                            <RadioSelector
                                radios={Object.entries(radioNames).map(([id, logo]) => ({ id, logo }))}
                                selected={selectedRadios}
                                setSelected={setSelectedRadios}
                            />
                          </div>

                          {(artist.songs.length > 0 || artist.songs_as_other.length > 0) && (
                          <div className="absolute right-4 -top-2 md:top-4 flex flex-col md:flex-row justify-between items-center">
                            {artist.songs.length > 0 && artist.songs_as_other.length > 0 ? (
                              <>
                                <span className="font-semibold text-center text-xs md:text-base md:mr-4">
                                  {viewMode === "lead" ? "Lead" : "Featured"}
                                </span>
                                <div
                                  className="flex justify-start items-center w-16 h-8 rounded-full p-1 cursor-pointer bg-accent/70 hover:bg-accent/90 transition-colors duration-300 ease-in-out"
                                  onClick={() => {
                                    setSelectedRadios([]);
                                    setViewMode(viewMode === "lead" ? "other" : "lead");
                                  }}
                                >
                                  <div
                                    className={`bg-white w-6 h-6 rounded-full shadow-md transform transition-transform ${
                                      viewMode === "other" ? "translate-x-8" : "translate-x-0"
                                    }`}
                                  ></div>
                                </div>
                              </>
                            ) : (
                              <span className="font-semibold text-center text-sm md:text-lg md:mr-2">
                                {artist.songs.length > 0 ? "Lead" : "Featured"} Artist
                              </span>
                            )}
                          </div>
                        )}
                        </div>

                        {artistStats && artistStats.different_songs_count > 0 && (
                          <StatsSummary
                            type="artist"
                            stats={{
                              total_plays: artistStats.total_plays,
                              different_songs_count: artistStats.different_songs_count,
                              selectedRadiosCount: selectedRadios.length,
                              totalRadios: Object.keys(radioNames).length,
                            }}
                            mostPlayed={artistStats.most_played}
                          />
                        )}
                      </div>

                      <div className="md:h-2/3 md:overflow-y-auto min-h-0 pt-2 px-4 pb-4">
                        {artistStats && <StatsCharts chartData={chartData}/>}
                      </div>

                    </div>
                  </div>
              }
            </>
        }
      </div>
    </Body>
  );
}
