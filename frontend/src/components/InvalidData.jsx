import {Link} from "react-router-dom";

import logo from "../assets/rlogo-raisinblack.png";

export default function InvalidData({ title, full=false }) {
    return (
    <div className={`${full ? 'h-[90vh] bg-primary/30 rounded-xl drop-shadow-2xl mt-[1.5vh] overflow-hidden' : 'h-[90vh] overflow-hidden'}`}>
        <div className="flex items-center justify-center text-center text-primary h-full min-h-0 relative">
            <div className="w-4/5 md:w-1/3 p-8 rounded-xl bg-accent/85 flex flex-col justify-center items-center">
                <img src={logo} alt="RSlogo" className="w-[200px] md:w-[250px]"/>
                <div className="mt-4 font-bold text-3xl md:text-5xl">404</div>
                <div className="font-bold text-3xl md:text-5xl">{title} Not Found</div>
                <div className="mt-4 text-lg md:text-2xl">The page you are looking for does not exist.</div>
                <div className="mt-4 w-32 p-2 btn-primary">
                    <Link to="/">Home</Link>
                </div>
                <div className="wave bottom-[50%] w-[215vw] md:w-[95vw] h-[215vw] md:h-[95vw]">
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
            </div>
        </div>
    </div>
    );
}