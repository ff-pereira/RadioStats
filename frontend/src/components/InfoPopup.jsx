import { useEffect } from "react";

import logo from "../assets/rlogo-raisinblack.png";

export default function InfoPopup({ isOpen, onClose }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {

      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="font-normal fixed inset-0 flex items-center justify-center bg-primary/75 z-50 text-primary" onClick={onClose}>
      <div
          className="p-6 md:p-8 bg-secondary rounded-3xl shadow-lg border-4 border-primary flex flex-col justify-center items-center relative"
          onClick={(e) => e.stopPropagation()}>
        <img src={logo} alt="RSlogo" className="mt-0.5 w-[75px] md:w-[100px]"/>
        <div className="text-xl font-semibold">RadioStats</div>
        <div className="text-base md:text-lg">Author: <strong>ffpereira</strong></div>
        <div className="text-base md:text-lg mb-4">Contact: <strong>radios@ffpereira.com</strong></div>
        <div
            className="bg-secondary rounded-md w-[75vw] md:w-[50vw] h-[55vh] md:h-[50vh] overflow-y-scroll font-normal p-1 md:p-4 text-justify space-y-2 md:space-y-8 text-sm md:text-base">
          <p>
            RadioStats is an <strong>open-source, independent analytical project</strong> that monitors and visualizes
            the most frequently played
            songs on Portuguese radio stations owned by the Bauer Media Group.
            Data is collected automatically and updated daily at 1 AM, reflecting the previous day’s broadcasts.
          </p>
          <p className="font-bold">
            This project is <span className="underline">not</span> affiliated, endorsed, or sponsored in any way by
            Bauer Media Group or its
            subsidiaries. All data is obtained from publicly accessible sources, and no personally identifiable
            information is collected, stored, or shared.
          </p>
          <p>
            Descriptions and nationalities of artists are produced automatically with artificial intelligence and are
            provided for informational purposes only.
            As such, they may contain inaccuracies or approximations. <strong>All songs, albums, and artists content remain the
            intellectual property of their respective owners.</strong>
          </p>
          <p>
            This project is strictly non-commercial, developed in accordance with <strong>best practices for data privacy
            and responsible usage</strong>, and intended solely for research and educational purposes.
            The author disclaims any liability for errors, omissions, or inaccuracies in the data presented.
          </p>
        </div>

        <svg xmlns="http://www.w3.org/2000/svg"
             className="absolute top-2 right-2 cursor-pointer hover:scale-110 ease-in-out duration-200"
             viewBox="0 0 640 640"
             fill="#252121" width="32" height="32"
             onClick={onClose}>
          <path
              d="M183.1 137.4C170.6 124.9 150.3 124.9 137.8 137.4C125.3 149.9 125.3 170.2 137.8 182.7L275.2 320L137.9 457.4C125.4 469.9 125.4 490.2 137.9 502.7C150.4 515.2 170.7 515.2 183.2 502.7L320.5 365.3L457.9 502.6C470.4 515.1 490.7 515.1 503.2 502.6C515.7 490.1 515.7 469.8 503.2 457.3L365.8 320L503.1 182.6C515.6 170.1 515.6 149.8 503.1 137.3C490.6 124.8 470.3 124.8 457.8 137.3L320.5 274.7L183.1 137.4z"/>
        </svg>

      </div>
    </div>
  );
}
