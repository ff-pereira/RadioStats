import { Link } from "react-router-dom";

import CircleMenu from "./CircleMenu.jsx";
import logo from "../assets/rlogo-sunglow.png";


export default function Header() {
    return (
        <header className="sticky top-0 bg-primary text-accent shadow-sm z-50 h-[65px] shadow-xl border-b-4 border-accent">
            <div className="grid grid-cols-2 items-center px-4 py-2 w-full">
                <div className="ml-6 w-[75px] md:w-[75px]">
                    <Link to="/">
                        <img src={logo} alt="radiologo"
                             className="mt-0.5 w-full hover:scale-105 ease-in-out duration-200"/>
                    </Link>
                </div>
                <div className="text-lg font-bold justify-self-end">
                    <CircleMenu />
                </div>
            </div>
        </header>
    );
}