import { memo } from 'react';
import Album from "./Album.jsx";
import {Link} from "react-router-dom";

export default memo(function Song({ song, albumSize, activeAlbumId, setActiveAlbumId, playCount=false }) {
  return (
    <div className="flex flex-col justify-center items-center">
        <Album id={song.id} imageUrl={song.album_cover_url} size={albumSize} audioUrl={song.sample}
               activeAlbumId={activeAlbumId} setActiveAlbumId={setActiveAlbumId} playCount={playCount}/>
        <div className="mt-1 font-semibold truncate hover:scale-105 ease-in-out duration-200">
            <Link to={`/song/${song.id}`}>{song.name}</Link>
        </div>
    </div>
  );
});