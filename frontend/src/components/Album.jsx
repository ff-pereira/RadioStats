import { useRef, useEffect, useState } from "react";
import albumImageFallback from "../assets/default.png";

export default function Album({ id, imageUrl, size, audioUrl, activeAlbumId, setActiveAlbumId, playCount=false }) {
  const audioRef = useRef(null);
  const [audioError, setAudioError] = useState(false);

  const [localPlaying, setLocalPlaying] = useState(false);
  const [imgSrc, setImgSrc] = useState(imageUrl || albumImageFallback);

  const isPlaying = activeAlbumId === id;

  useEffect(() => {
    if (isPlaying) {
      audioRef.current.play();
      setLocalPlaying(true);
    } else if (localPlaying) {
      setLocalPlaying(false);
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  }, [isPlaying]);

  const handleClick = () => {
    if (audioError) return;
    if (isPlaying) setActiveAlbumId(null);
    else setActiveAlbumId(id);
  };

  return (
    <div className={`aspect-square album ${size === "normal" ? "normal" : ""} 
                    ${size === "small" ? "small" : ""} 
                    ${size === "very-small" ? "very-small" : ""} 
                    ${localPlaying ? "playing" : ""} ${audioError ? "broken" : ""}`} data-cover-url={imageUrl} onClick={handleClick}>
      <div className="cover">
        {playCount &&
            <div className="absolute top-0 right-0 py-1 w-12 text-center m-2 bg-accent font-semibold border border-primary rounded-md">
              {playCount}
            </div>
        }
        <img src={imgSrc} alt="Album Cover" onError={() => setImgSrc(albumImageFallback)}/>
      </div>
      <div className="vinyl">
        <div className="vinyl-cover" style={{ backgroundImage: `url(${imgSrc})` }}/>
      </div>
      <audio ref={audioRef} src={audioUrl} onError={() => setAudioError(true)} onEnded={() => setActiveAlbumId(null)} />
    </div>
  );
}
