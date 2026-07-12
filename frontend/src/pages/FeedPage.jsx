import {useEffect, useState} from 'react';

import Plays from '../components/Plays';
import Artists from '../components/Artists';
import { useApi } from '../contexts/ApiProvider';
import InputField from "../components/InputField.jsx";
import RadioSelector from '../components/RadioSelector';
import DualRangeSlider from '../components/DualRangeSlider';
import { useDebounce } from '../hooks/useDebounce.jsx';


export default function FeedPage() {
    const api = useApi();

    const [stats, setStats] = useState(null);
    const [range, setRange] = useState([]);
    const [radios, setRadios] = useState([]);
    const [songSearch, setSongSearch] = useState('');
    const [artistSearch, setArtistSearch] = useState('');
    const [showArtists, setShowArtists] = useState(false);
    const [selectedRadios, setSelectedRadios] = useState([]);
    const [interval, setInterval] = useState({ startDate: null, endDate: null });

    const debouncedSongSearch = useDebounce(songSearch, 200);
    const debouncedArtistSearch = useDebounce(artistSearch, 200);

    useEffect(() => {
        (async () => {
            const response = await api.get("/radios");
            if (response.ok) {
                setRadios(response.body);
            } else {
                setRadios([]);
                setSelectedRadios([]);
            }
        })();
    }, [api]);

    useEffect(() => {
        (async () => {
            const response = await api.get('/interval');
            if (response.ok) {
                setInterval({
                    startDate: response.body.first_play,
                    endDate: response.body.last_play,
                });
                setRange([0, Math.ceil((new Date(response.body.last_play) - new Date(response.body.first_play)) / (1000 * 60 * 60 * 24))]);
            }
        })();
    }, [api]);

    useEffect(() => {
     if (!interval.startDate || !interval.endDate || range.length !== 2) return;

      (async () => {
        const afterDate = new Date(interval.startDate);
        afterDate.setDate(afterDate.getDate() + range[0]);
        const beforeDate = new Date(interval.startDate);
        beforeDate.setDate(beforeDate.getDate() + range[1]);

        let query = '';
        if (selectedRadios.length > 0) {
          query += `?radios=${selectedRadios.join(',')}`;
        } else {
          query += '?';
        }
        query += `&after=${afterDate.toISOString().slice(0, 10)}&before=${beforeDate.toISOString().slice(0, 10)}`;
        if (songSearch) query += `&song_search=${encodeURIComponent(debouncedSongSearch)}`;
        if (artistSearch) query += `&artist_search=${encodeURIComponent(debouncedArtistSearch)}`;

        const response = await api.get(`/stats${query}`);
        if (response.ok) {
          setStats({
            differentSongs: response.body.total_different_songs,
            totalPlays: response.body.total_plays,
          });
        }

      })();
    }, [api, selectedRadios, range, interval, debouncedSongSearch, debouncedArtistSearch]);

    const handleRangeChange = (newRange) => {
        setRange(newRange);
    };

    return (
        <div className="bg-primary/30 rounded-xl drop-shadow-2xl p-4">
            {interval.startDate === null && interval.endDate === null ?
                <div className="h-[95%] w-full flex justify-center items-center">
                    <div className="spinner"></div>
                </div>
            :
                <>
                    <RadioSelector radios={radios} selected={selectedRadios} setSelected={setSelectedRadios}/>

                    <div className="mt-2 grid grid-cols-2 md:grid-cols-4 bg-accent/75 rounded-xl p-2 ">
                        <div className="flex flex-col justify-center items-center border-r border-primary/25">
                            <div className="text-sm md:text-base">Total Days</div>
                            <div
                                className="text-lg md:text-xl font-semibold">{range.length === 2 ? (range[1] - range[0]) : 0} days
                            </div>
                        </div>
                        <div className="flex flex-col justify-center items-center md:border-r md:border-primary/25">
                            <div className="text-sm md:text-base">Total Radios Selected</div>
                            <div className="text-lg md:text-xl font-semibold">{selectedRadios.length > 0 ? selectedRadios.length : radios.length}</div>
                        </div>
                        <div className="flex flex-col justify-center items-center border-r border-primary/25">
                            <div className="text-sm md:text-base">Total Plays</div>
                            <div className="text-lg md:text-xl font-semibold">
                                {stats === null ? 0 : stats.totalPlays}
                            </div>
                        </div>
                        <div className="flex flex-col justify-center items-center">
                            <div className="text-sm md:text-base">Total Different Songs</div>
                            <div className="text-lg md:text-xl font-semibold">
                                {stats === null ? 0 : stats.differentSongs}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 md:gap-6">
                        <InputField name="songSearch" placeholder="Song Search" type="text" value={songSearch}
                                    onChange={e => setSongSearch(e.target.value)}></InputField>
                        <InputField name="artistSearch" placeholder="Artist Search" type="text" value={artistSearch}
                                    onChange={e => setArtistSearch(e.target.value)}></InputField>
                    </div>

                    <DualRangeSlider
                        startDate={interval.startDate}
                        endDate={interval.endDate}
                        onChange={handleRangeChange}
                    />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className={`h-[51vh] md:h-[64.2vh] overflow-y-auto rounded-xl with-scrollbar ${showArtists ? 'hidden md:block' : 'block'}`}>
                            <Plays content="top" selectedIds={selectedRadios} range={range} startDate={interval.startDate} songSearch={debouncedSongSearch} artistSearch={debouncedArtistSearch}/>
                        </div>
                        <div className={`h-[51vh] md:h-[64.2vh] overflow-y-auto rounded-xl with-scrollbar ${showArtists ? 'block' : 'hidden md:block'}`}>
                            <Artists content="top" selectedIds={selectedRadios} range={range} startDate={interval.startDate} songSearch={debouncedSongSearch} artistSearch={debouncedArtistSearch}/>
                        </div>
                        <div className="-mt-2 md:hidden flex justify-center items-center">
                            <button onClick={() => setShowArtists(false)}
                                className={`py-1 rounded-l-xl font-semibold transition w-1/2 ${
                                    !showArtists ? 'bg-primary text-white' : 'bg-accent text-primary'}`}>
                                Songs
                            </button>
                            <button onClick={() => setShowArtists(true)}
                                className={`py-1 rounded-r-xl font-semibold transition w-1/2 ${
                                    showArtists ? 'bg-primary text-white' : 'bg-accent text-primary'}`}>
                                Artists
                            </button>
                        </div>
                    </div>
                </>
            }
        </div>
    );
}
