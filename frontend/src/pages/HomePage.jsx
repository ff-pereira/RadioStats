import {useState} from "react";

import Body from '../components/Body';
import FeedPage from "./FeedPage.jsx";
import logo from "../assets/rlogo-raisinblack.png";
import InfoPopup from "../components/InfoPopup.jsx";

export default function HomePage() {
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const togglePopup = () => {
        setIsPopupOpen(!isPopupOpen);
    };

    return (
        <Body>
            <InfoPopup isOpen={isPopupOpen} onClose={togglePopup} />

            <div className="h-screen pt-[25vh] md:pt-[15vh]">
                <svg xmlns="http://www.w3.org/2000/svg"
                     viewBox="0 0 640 640" fill="currentColor"
                     className="absolute top-4 right-4 hover:scale-110 ease-in-out duration-200 w-12 text-accent hover:text-primary cursor-pointer"
                     data-label="Info" onClick={togglePopup}>
                    <path d="M320 576C461.4 576 576 461.4 576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320C64 461.4 178.6 576 320 576zM288 224C288 206.3 302.3 192 320 192C337.7 192 352 206.3 352 224C352 241.7 337.7 256 320 256C302.3 256 288 241.7 288 224zM280 288L328 288C341.3 288 352 298.7 352 312L352 400L360 400C373.3 400 384 410.7 384 424C384 437.3 373.3 448 360 448L280 448C266.7 448 256 437.3 256 424C256 410.7 266.7 400 280 400L304 400L304 336L280 336C266.7 336 256 325.3 256 312C256 298.7 266.7 288 280 288z"/>
                </svg>
                <div className="bg-accent/85 p-6 rounded-md flex flex-col justify-center items-center mx-auto w-fit text-primary shadow-lg">
                    <img src={logo} alt="radiologo" className="w-[200px] md:w-[300px]"/>
                    <div className="mt-2 text-center text-4xl md:text-5xl font-bold">RadioStats</div>
                    <div className="mt-4">Developed by:</div>
                    <div className="text-2xl font-semibold">ffpereira</div>
                </div>

                <div className="mt-[15vh] md:mt-[35vh] text-xl text-center animate-bounce flex justify-center items-center gap-2"
                    onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })}>
                    <div className="cursor-pointer bg-accent/85 flex justify-center items-center p-2 rounded-full shadow-lg font-bold hover:bg-secondary/85 hover:scale-110 ease-in-out duration-200">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                             stroke="currentColor" className="w-8 h-8" strokeWidth="2px">
                            <path d="M19.5 13.5 12 21m0 0-7.5-7.5M12 21V3"/>
                        </svg>
                    </div>
                </div>

                <div className="wave bottom-0 w-[95vw] h-[95vw] overflow-x-hidden">
                    <svg version="1.1" viewBox="0 0 500 500" preserveAspectRatio="xMinYMin meet">
                        {Array.from({length: 7}).map((_, i) => (
                            <circle key={i} cx="250" cy="250" r="200" fillOpacity="0" strokeWidth="1px"
                                    className="stroke-primary">
                                <animate attributeName="r" from="0" to="200" dur="8s" repeatCount="indefinite"
                                         begin={`${(i * 1.14).toFixed(2)}s`}/>
                            </circle>
                        ))}
                    </svg>
                </div>
                <div className="text-primary absolute bottom-2 left-4"></div>
                <div className="text-primary absolute bottom-2 right-4">Version 1.0.3</div>
            </div>

            <div className="h-screen pt-[2.5vh]">
                <FeedPage/>
            </div>
        </Body>
    );
}