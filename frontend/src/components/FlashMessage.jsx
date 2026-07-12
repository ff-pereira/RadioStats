import { useContext } from 'react';
import { FlashContext } from '../contexts/FlashProvider';

export default function FlashMessage() {
    const { flashMessage, visible, hideFlash } = useContext(FlashContext);

    const variantColors = {
        info: 'bg-blue-100 text-blue-800 border-blue-300',
        success: 'bg-green-100 text-green-800 border-green-300',
        warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        danger: 'bg-red-100 text-red-800 border-red-300',
    };
    const colors = variantColors[flashMessage.type] || variantColors.info;

    return (
        <div className={`transition-all duration-300 ease-in-out transform ${visible ? 'opacity-100 max-h-40' : 'opacity-0 max-h-0 overflow-hidden'}`}>
            <div className={`relative px-4 py-3 border rounded-md ${colors} shadow-md`}>
                <span>{flashMessage.message}</span>
                <button onClick={hideFlash} className="absolute top-2 right-2 text-lg font-bold text-current hover:text-gray-700">&times;</button>
            </div>
        </div>
    );
}