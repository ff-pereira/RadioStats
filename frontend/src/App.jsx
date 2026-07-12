import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import FlashProvider from "./contexts/FlashProvider";
import ApiProvider from "./contexts/ApiProvider";
import Header from './components/Header';
import HomePage from "./pages/HomePage";
import FeedPage from "./pages/FeedPage";
import SongPage from "./pages/SongPage.jsx";
import ArtistPage from "./pages/ArtistPage.jsx";
import RadioPage from "./pages/RadioPage.jsx";
import ScrollToTop from "./components/ScrollToTop.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";
import EditPage from "./pages/EditPage.jsx";


function AppContent() {
    const location = useLocation();
    const showHeader = location.pathname !== '/';
    return (
        <>
            {showHeader && <Header />}
            <ScrollToTop />
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/feed" element={<FeedPage />} />
                <Route path="/edit" element={<EditPage />} />
                <Route path="/radio/:radio_id" element={<RadioPage />} />
                <Route path="/song/:song_id" element={<SongPage />} />
                <Route path="/artist/:artist_id" element={<ArtistPage />} />
                <Route path="*" element={<NotFoundPage />} />
            </Routes>
        </>
    );
}

export default function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <FlashProvider>
                    <ApiProvider>
                        <AppContent />
                    </ApiProvider>
                </FlashProvider>
            </BrowserRouter>
        </div>
    );
}
