import { memo } from 'react';
import Album from "./Album.jsx";
import {Link} from "react-router-dom";

export default memo(function Play({ play, albumSize,  activeAlbumId, setActiveAlbumId }) {
  return (
    <div className="flex flex-col">
        <div className="bg-gray-100 hover:bg-gray-200 p-2 border-b border-gray-300 grid grid-cols-4 md:grid-cols-5">
            <div className="flex justify-center items-center">
                <Album id={play.id} imageUrl={play.album_cover_url} size={albumSize} audioUrl={play.sample}
                       activeAlbumId={activeAlbumId} setActiveAlbumId={setActiveAlbumId}/>
            </div>
            <div className="col-span-2 flex flex-col justify-center items-center px-2 md:px-0">
                <div className="font-semibold hover:scale-105 ease-in-out duration-200 whitespace-normal text-center">
                    <Link to={`/song/${play.id}`} >{play.song_name}</Link>
                </div>

                <div className="text-sm hover:scale-105 ease-in-out duration-200 text-sm md:text-base">
                    <Link to={`/artist/${play.artist_id}`}>{play.artist_name}</Link>
                </div>
            </div>
            <div className="flex justify-center items-center">
                <div className="text-xl md:text-2xl">{play.play_count}</div>
            </div>
            <div className="hidden md:flex flex-col justify-center items-center">
                <div className="font-semibold">Avg per Day</div>
                <div className="text-lg">{play.avg_per_day}</div>
            </div>
        </div>
    </div>
  );
});
