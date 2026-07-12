import { memo } from 'react';
import {Link} from "react-router-dom";

export default memo(function Artist({ artist }) {
  return (
    <div className="flex flex-col">
        <div className="bg-gray-100 hover:bg-gray-200 p-2 border-b border-gray-300 grid grid-cols-5 md:grid-cols-6">
            <div className="col-span-2 flex flex-col justify-center items-center px-2 md:px-0">
                <div className="font-semibold hover:scale-105 ease-in-out duration-200 whitespace-normal text-center">
                    <Link to={`/artist/${artist.id}`}>{artist.name}</Link>
                </div>
            </div>
            <div className="flex flex-col justify-center items-center text-sm md:text-base">
                <div className="font-semibold">Lead</div>
                <div>{artist.lead.play_count} Plays</div>
                <div>{artist.lead.songs} Songs</div>
            </div>
            <div className="flex flex-col justify-center items-center text-sm md:text-base">
                <div className="font-semibold">Featured</div>
                <div>{artist.other.play_count} Plays</div>
                <div>{artist.other.songs} Songs</div>
            </div>
            <div className="flex justify-center items-center">
                <div className="text-xl md:text-2xl">{artist.count}</div>
            </div>
            <div className="hidden md:flex flex-col justify-center items-center">
                <div className="font-semibold">Avg per day</div>
                <div className="text-lg">{artist.avg_per_day}</div>
            </div>
        </div>
    </div>
  );
});
