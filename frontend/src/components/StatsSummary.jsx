import { Link } from "react-router-dom";

export default function StatsSummary({ type, stats, mostPlayed, countsByRadio }) {
  return (
    <div className="mt-2.5 md:mt-0 col-span-full grid grid-cols-4 bg-accent/75 rounded-xl p-2">
      <div className={`col-span-full grid ${type === "song" ? "grid-cols-2 md:grid-cols-3" : "grid-cols-3"} border-b border-primary/25 pb-2`}>

        {type === "song" && (
          <>
            <div className="flex flex-col justify-center items-center border-r border-primary/25 mr-2">
              <div className="text-xs md:text-base">Total Plays</div>
              <div className="font-bold text-lg md:text-3xl">{stats.total_plays}</div>
            </div>
            <div className="flex flex-col justify-center items-center md:border-r md:border-primary/25 md:mr-2">
              <div className="text-xs md:text-base">Different Radios</div>
              <div className="font-bold text-lg md:text-3xl">{stats.different_radios_count}</div>
            </div>
            <div className="mt-1 md:mt-0 col-span-2 md:col-span-1 flex flex-col justify-center items-center">
              <div className="hidden md:block md:text-base">Counts by Radio Name</div>
              <div className="h-10 md:h-9 overflow-y-auto overflow-x-visible w-[90%]">
                {countsByRadio.map(({ radio_id, count, name }) => (
                  <div key={radio_id} className="flex justify-between -my-1">
                    <Link
                      to={`/radio/${radio_id}`}
                      className="font-semibold hover:scale-95 ease-in-out duration-200"
                    >
                      {name}
                    </Link>
                    <div>{count}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
        {type === "radio" && (
          <>
            <div className="flex flex-col justify-center items-center border-r border-primary/25 mr-2">
              <div className="text-xs md:text-base">Total Plays</div>
              <div className="font-bold text-lg md:text-3xl">{stats.total_plays}</div>
            </div>
            <div className="flex flex-col justify-center items-center border-r border-primary/25 mr-2">
              <div className="text-xs md:text-base">Different Songs</div>
              <div className="font-bold text-lg md:text-3xl">{stats.different_songs_count}</div>
            </div>
            <div className="flex flex-col justify-center items-center">
              <div className="text-xs md:text-base">Avg Plays per Song</div>
              <div className="font-bold text-lg md:text-3xl">{stats.avg_plays_per_song}</div>
            </div>
          </>
        )}
        {type === "artist" && (
          <>
            <div className="flex flex-col justify-center items-center border-r border-primary/25 mr-2">
              <div className="text-xs md:text-base">Radios</div>
              <div className="font-bold text-lg md:text-3xl">
                {stats.selectedRadiosCount || stats.totalRadios}
              </div>
            </div>
            <div className="flex flex-col justify-center items-center border-r border-primary/25 mr-2">
              <div className="text-xs md:text-base">Plays</div>
              <div className="font-bold text-lg md:text-3xl">{stats.total_plays}</div>
            </div>
            <div className="flex flex-col justify-center items-center">
              <div className="text-xs md:text-base">Different Songs</div>
              <div className="font-bold text-lg md:text-3xl">{stats.different_songs_count}</div>
            </div>
          </>
        )}
      </div>

      {["day", "week", "month", "year"].map((period, index) => (
        <div
          key={period}
          className={`md:mt-2 pt-2 col-span-2 md:col-span-1 flex flex-col justify-center items-center md:border-r border-primary/25 last:border-0
            ${period === "week" ? "border-r-0 md:border-r" : ""}
            ${index < 2 ? "border-b border-primary/25 md:border-b-0" : ""}`}
        >
          <div className="text-sm md:text-base">
            Most Played {period.charAt(0).toUpperCase() + period.slice(1)}
          </div>
          <div className="font-bold text-xl md:text-3xl">
            {mostPlayed[period][0].count}
          </div>
          <div
            className={
              mostPlayed[period].length > 1
                ? "h-8 flex flex-col overflow-y-scroll"
                : "h-8 flex justify-center items-center gap-2"
            }
          >
            {mostPlayed[period].map((mp) => (
              <div
                key={mp.value}
                className={`mt-0 ${period === "week" ? "text-xs md:text-sm" : "text-sm"}`}
              >
                {mp.value}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}