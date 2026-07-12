import { useEffect, useState } from "react";
import Body from "../components/Body.jsx";
import { useApi } from "../contexts/ApiProvider.jsx";

const DataTable = ({ title, columns, children }) => (
  <div className="m-6 rounded-xl overflow-hidden border border-primary">
    {title && <h3 className="px-4 py-2 bg-accent font-semibold text-lg">{title}</h3>}
    <div className="overflow-auto max-h-[calc(100vh-9rem)]">
      <table className="w-full table-auto border-collapse">
        <thead className="bg-accent font-semibold sticky top-0 z-20">
          <tr>
            {columns.map((col) => (
              <th key={col} className="border border-primary px-4 py-2">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  </div>
);


const ActionInput = ({ id, value, onChange, onAction, loading, placeholder }) => (
  <div className="flex flex-col">
    <div className="flex items-center gap-2">
      <input
        id={id}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input-field h-8 w-full"
      />
      <button
        onClick={onAction}
        disabled={loading}
        className="btn-accent p-2 h-8 flex justify-center items-center"
      >
        {loading ? "Processing..." : "Submit"}
      </button>
    </div>
  </div>
);


const SongRow = ({ item, value, error, loading, onChange, onConvert }) => {
  const inputId = `song-${item.item_code}-${item.song_name}`; // unique id
  return (
    <tr className="hover:bg-gray-200">
      <td className="border border-primary px-4 py-1.5 text-center bg-white">{item.plays_count}</td>
      <td className="border border-primary px-4 py-1.5 bg-white">{item.song_name}</td>
      <td className="border border-primary px-4 py-1.5 bg-white">{item.artist_name}</td>
      <td className="border border-primary px-4 py-1.5 bg-white">
        <ActionInput
          id={inputId}
          name={inputId}
          value={value ?? ""}
          onChange={onChange}
          onAction={onConvert}
          loading={loading}
          placeholder="Song ID"
        />
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      </td>
    </tr>
  );
};


const ArtistRow = ({ item, updateValues, error, loading, onChange, onUpdate }) => {
  const natId = `artist-${item.artist_id}-nationality`;
  const descId = `artist-${item.artist_id}-description`;

  return (
    <tr className="hover:bg-gray-200">
      <td className="border border-primary px-4 py-1.5 text-center bg-white">{item.plays_count}</td>
      <td className="border border-primary px-4 py-1.5 bg-white">{item.artist_name}</td>
      <td className="border border-primary px-4 py-1.5 bg-white">
        <input
          type="text"
          id={natId}
          name={natId}
          placeholder="Nationality"
          value={updateValues.nationality ?? item.nationality ?? ""}
          onChange={(e) => onChange("nationality", e.target.value)}
          className="input-field w-full h-8"
        />
        <input
          type="text"
          id={descId}
          name={descId}
          placeholder="Description"
          value={updateValues.description ?? item.description ?? ""}
          onChange={(e) => onChange("description", e.target.value)}
          className="input-field w-full mt-1 h-8"
        />
      </td>
      <td className="border border-primary px-4 py-1.5 bg-white">
        <button
          onClick={onUpdate}
          disabled={loading}
          className="btn-accent p-2 h-8 flex justify-center items-center"
        >
          {loading ? "Updating..." : "Update"}
        </button>
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      </td>
    </tr>
  );
};


export default function EditPage() {
  const api = useApi();
  const [noMcrData, setNoMcrData] = useState();
  const [songIds, setSongIds] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  const [artistUpdates, setArtistUpdates] = useState({});
  const [noDescriptionArtists, setNoDescriptionArtists] = useState();

  useEffect(() => {
    (async () => {
      const res = await api.get(`/no_mcr_top`);
      if (res.ok) setNoMcrData(res.body);
    })();
    (async () => {
      const res = await api.get(`/no_description_top`);
      if (res.ok) setNoDescriptionArtists(res.body);
    })();
  }, [api]);

  const handleChange = (itemCode, value) => {
    setSongIds(prev => ({ ...prev, [itemCode]: value }));
    setErrors(prev => ({ ...prev, [itemCode]: undefined }));
  };

  const handleArtistChange = (artistId, field, value) => {
    setArtistUpdates(prev => ({ ...prev, [artistId]: { ...prev[artistId], [field]: value } }));
  };

  const handleConvert = async (itemCode) => {
    const raw = (songIds[itemCode] ?? "").toString().trim();
    const songId = Number(raw);
    if (!raw || !Number.isInteger(songId) || songId <= 0) {
      setErrors(prev => ({ ...prev, [itemCode]: "Enter a valid positive integer song id" }));
      return;
    }
    setLoading(prev => ({ ...prev, [itemCode]: true }));
    setErrors(prev => ({ ...prev, [itemCode]: undefined }));
    try {
      const res = await api.post(`/no_mcr_to_play/${encodeURIComponent(itemCode)}/${songId}`);
      if (res.ok) {
        setNoMcrData(prev => prev.filter(item => item.item_code !== itemCode));
        setSongIds(prev => { const copy = { ...prev }; delete copy[itemCode]; return copy; });
      } else {
        setErrors(prev => ({ ...prev, [itemCode]: res.body?.message || "Conversion failed" }));
      }
    } catch {
      setErrors(prev => ({ ...prev, [itemCode]: "Network error" }));
    } finally {
      setLoading(prev => ({ ...prev, [itemCode]: false }));
    }
  };

  const handleUpdateArtist = async (artistId) => {
    const updateData = artistUpdates[artistId] || {};
    const payload = Object.fromEntries(Object.entries(updateData).filter(([_, v]) => v?.toString().trim()));
    if (!Object.keys(payload).length) return;

    setLoading(prev => ({ ...prev, [artistId]: true }));
    setErrors(prev => ({ ...prev, [artistId]: undefined }));

    try {
      const res = await api.post(`/update_artist/${artistId}`, payload);
      if (res.ok) {
      setNoDescriptionArtists(prev => prev.map(a => a.artist_id === artistId ? { ...a, ...payload } : a));
      setArtistUpdates(prev => {const copy = { ...prev };delete copy[artistId];return copy;});
    } else {
        setErrors(prev => ({ ...prev, [artistId]: res.body?.message || "Update failed" }));
      }
    } catch {
      setErrors(prev => ({ ...prev, [artistId]: "Network error" }));
    } finally {
      setLoading(prev => ({ ...prev, [artistId]: false }));
    }
  };

  return (
    <Body>
        { noMcrData === undefined || noDescriptionArtists === undefined ?
            <div className="h-[90vh] w-full flex justify-center items-center">
                <div className="spinner"></div>
            </div>
        :
          <div className="h-[90vh] bg-primary/30 rounded-xl drop-shadow-2xl mt-[1.5vh] overflow-auto">
            <div className="h-full grid grid-cols-1 md:grid-cols-2 md:gap-2 relative">

              <DataTable title="Songs without MCR" columns={["Count", "Title", "Artist", "Convert"]}>
                {noMcrData.map(item => (
                  <SongRow
                    key={`${item.item_code}-${item.song_name}`}
                    item={item}
                    value={songIds[item.item_code]}
                    error={errors[item.item_code]}
                    loading={loading[item.item_code]}
                    onChange={(val) => handleChange(item.item_code, val)}
                    onConvert={() => handleConvert(item.item_code)}
                  />
                ))}
              </DataTable>

              <DataTable title="Artists without Description/Nationality" columns={["Count", "Artist", "Data", "Update"]}>
                {noDescriptionArtists.map(item => {
                  const updateValues = artistUpdates[item.artist_id] || {};
                  return (
                    <ArtistRow
                      key={item.artist_id}
                      item={item}
                      updateValues={updateValues}
                      error={errors[item.artist_id]}
                      loading={loading[item.artist_id]}
                      onChange={(field, val) => handleArtistChange(item.artist_id, field, val)}
                      onUpdate={() => handleUpdateArtist(item.artist_id)}
                    />
                  );
                })}
              </DataTable>

            </div>
          </div>
        }
    </Body>
  );
}
