import Artist from './Artist';
import MostPlayed from "./MostPlayed.jsx";

export default function Artists({ content, selectedIds, range, startDate, songSearch, artistSearch }) {
  const urlBase = content === 'top' || content === undefined ? '/artists/most_played' : '/artists';

  const queryParams = [];
  if (selectedIds?.length) queryParams.push(`radios=${selectedIds.join(',')}`);
  if (range?.length === 2) {
    const formatDate = (daysOffset) => {
      const start = new Date(startDate);
      start.setDate(start.getDate() + daysOffset);
      return start.toISOString().split('T')[0];
    };
    queryParams.push(`after=${formatDate(range[0])}`, `before=${formatDate(range[1])}`);
  }
  if (songSearch) queryParams.push(`song_search=${encodeURIComponent(songSearch)}`);
  if (artistSearch) queryParams.push(`artist_search=${encodeURIComponent(artistSearch)}`);

  return (
    <MostPlayed
      urlBase={urlBase}
      queryParams={queryParams}
      renderItem={(artist) => <Artist key={artist.id} artist={artist} />}
    />
  );
}
