import React, { useState, useEffect } from 'react';

export default function DualRangeSlider({ startDate, endDate, onChange }) {
    const [minValue, setMinValue] = useState(0);
    const [maxValue, setMaxValue] = useState(0);
    const [totalDays, setTotalDays] = useState(0);

    useEffect(() => {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)); // Calculate total days
        setTotalDays(days);
        setMinValue(0);
        setMaxValue(days);
    }, [startDate, endDate]);

    const handleMinChange = (e) => {
        const value = Math.min(Number(e.target.value), maxValue - 1);
        setMinValue(value);
    };

    const handleMaxChange = (e) => {
        const value = Math.max(Number(e.target.value), minValue + 1);
        setMaxValue(value);
    };

    const handleInteractionEnd = () => {
        onChange && onChange([minValue, maxValue]);
    };

    const formatDate = (daysOffset) => {
        const start = new Date(startDate);
        const resultDate = new Date(start.setDate(start.getDate() + daysOffset));
        return resultDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    };

    return (
        <div className="dual-range-slider my-1 md:my-5">
            <input
                type="range"
                min={0}
                max={totalDays}
                value={minValue}
                onChange={handleMinChange}
                onMouseUp={handleInteractionEnd}
                onTouchEnd={handleInteractionEnd}
                className="thumb thumb-left"
            />
            <input
                type="range"
                min={0}
                max={totalDays}
                value={maxValue}
                onChange={handleMaxChange}
                onMouseUp={handleInteractionEnd}
                onTouchEnd={handleInteractionEnd}
                className="thumb thumb-right"
            />
            <div className="slider">
                <div className="slider-track"></div>
                <div
                    className="slider-range"
                    style={{
                        left: `${(minValue / totalDays) * 100}%`,
                        right: `${100 - (maxValue / totalDays) * 100}%`,
                    }}
                ></div>
            </div>
            <div className="flex justify-between mt-2 text-sm text-white font-bold">
                <div>{formatDate(minValue)} 00:00:00</div>
                <div>{formatDate(maxValue)} 00:00:00</div>
            </div>
        </div>
    );
}