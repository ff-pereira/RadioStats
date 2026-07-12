export default function RadioSelector({ radios, selected, setSelected }) {
  const toggleSelect = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex flex-wrap gap-4 justify-center items-center">
      {radios.map((radio) => (
        <label key={radio.id} className="flex items-center gap-2 transition ease-in-out duration-200 hover:scale-105 cursor-pointer">
          <input
            id={`radio-select-${radio.id}`}
            type="checkbox"
            className="w-5 h-5 cursor-pointer  accent-[#FFD13E]"
            checked={selected.includes(radio.id)}
            onChange={() => toggleSelect(radio.id)}
          />
          <img
            src={radio.logo}
            alt={`Radio ${radio.id}`}
            className="h-12 w-12 object-cover rounded-md"
          />
        </label>
      ))}
    </div>
  );
}