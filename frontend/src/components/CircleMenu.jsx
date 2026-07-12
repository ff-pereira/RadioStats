import React, {useState, useRef, useEffect} from "react";

import { gsap } from "gsap";
import {Link} from "react-router-dom";
import InfoPopup from "./InfoPopup.jsx";

export default function CircleMenu() {
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const circles = useRef([]);
  const labelRef = useRef(null);
  const menuRef = useRef(null);

  const togglePopup = () => {
    setIsPopupOpen(!isPopupOpen);
  };

  const openMenu = () => {
    const reversed = [...circles.current].reverse();
    reversed.forEach((el, i) => {
      const radius = el.offsetWidth;
      gsap.to(el, {
        top: -radius / 2,
        right: -radius / 2,
        delay: 0.1 * i,
        duration: 0.3,
      });
    });
    gsap.to(".hamburger", { top: -120, right: -120, duration: 0.5 });
  };

  const closeMenu = () => {
    circles.current.forEach((el, i) => {
      const radius = el.offsetWidth;
      gsap.to(el, {
        top: -radius,
        right: -radius,
        delay: 0.1 * i,
        duration: 0.4,
      });
    });
    gsap.to(".hamburger", { top: -60, right: -60, duration: 0.3 });
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        closeMenu();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
      <div className="menu-container" ref={menuRef}>
        <div className="outer-vinyl" ref={(el) => (circles.current[0] = el)}></div>
        <div className="medium-circle circle" ref={(el) => (circles.current[1] = el)}></div>
        <div className="small-circle circle" ref={(el) => (circles.current[2] = el)}>

          <svg xmlns="http://www.w3.org/2000/svg"
               viewBox="0 0 640 640" fill="currentColor" className="icon home-icon hover:scale-110 ease-in-out duration-200"
               data-label="Info" onClick={togglePopup}>
            <path
                d="M320 576C461.4 576 576 461.4 576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320C64 461.4 178.6 576 320 576zM288 224C288 206.3 302.3 192 320 192C337.7 192 352 206.3 352 224C352 241.7 337.7 256 320 256C302.3 256 288 241.7 288 224zM280 288L328 288C341.3 288 352 298.7 352 312L352 400L360 400C373.3 400 384 410.7 384 424C384 437.3 373.3 448 360 448L280 448C266.7 448 256 437.3 256 424C256 410.7 266.7 400 280 400L304 400L304 336L280 336C266.7 336 256 325.3 256 312C256 298.7 266.7 288 280 288z"/>
          </svg>

          <Link to="/">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor"
                 className="icon search-icon hover:scale-110 ease-in-out duration-200"
                 viewBox="0 0 640 640"
                 data-label="Home">
              <path
                  d="M341.8 72.6C329.5 61.2 310.5 61.2 298.3 72.6L74.3 280.6C64.7 289.6 61.5 303.5 66.3 315.7C71.1 327.9 82.8 336 96 336L112 336L112 512C112 547.3 140.7 576 176 576L464 576C499.3 576 528 547.3 528 512L528 336L544 336C557.2 336 569 327.9 573.8 315.7C578.6 303.5 575.4 289.5 565.8 280.6L341.8 72.6zM304 384L336 384C362.5 384 384 405.5 384 432L384 528L256 528L256 432C256 405.5 277.5 384 304 384z"/>
            </svg>
          </Link>

          <InfoPopup isOpen={isPopupOpen} onClose={togglePopup} />
        </div>

        <div className="close" onClick={closeMenu}>
          <svg xmlns="http://www.w3.org/2000/svg"
               className="hover:scale-110 ease-in-out duration-200"
               viewBox="0 0 640 640"
               fill="#252121" width="32" height="32"
               style={{position: "absolute", bottom: 20, left: 20}}>
            <path
                d="M183.1 137.4C170.6 124.9 150.3 124.9 137.8 137.4C125.3 149.9 125.3 170.2 137.8 182.7L275.2 320L137.9 457.4C125.4 469.9 125.4 490.2 137.9 502.7C150.4 515.2 170.7 515.2 183.2 502.7L320.5 365.3L457.9 502.6C470.4 515.1 490.7 515.1 503.2 502.6C515.7 490.1 515.7 469.8 503.2 457.3L365.8 320L503.1 182.6C515.6 170.1 515.6 149.8 503.1 137.3C490.6 124.8 470.3 124.8 457.8 137.3L320.5 274.7L183.1 137.4z"/>
          </svg>
        </div>

        <div className="hamburger" onClick={openMenu}>
          <svg xmlns="http://www.w3.org/2000/svg" className="hover:scale-110 ease-in-out duration-200" fill="#FFD13E" viewBox="0 0 640 640" width="36" height="36"
               style={{position: "absolute", bottom: 10, left: 12}}>
            <path
                d="M96 160C96 142.3 110.3 128 128 128L512 128C529.7 128 544 142.3 544 160C544 177.7 529.7 192 512 192L128 192C110.3 192 96 177.7 96 160zM96 320C96 302.3 110.3 288 128 288L512 288C529.7 288 544 302.3 544 320C544 337.7 529.7 352 512 352L128 352C110.3 352 96 337.7 96 320zM544 480C544 497.7 529.7 512 512 512L128 512C110.3 512 96 497.7 96 480C96 462.3 110.3 448 128 448L512 448C529.7 448 544 462.3 544 480z"/>
          </svg>
        </div>

        <div className="label" ref={labelRef}></div>
      </div>
  );
}
