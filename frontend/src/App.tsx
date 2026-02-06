import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Home } from './pages/Home';
import { VideoList } from './pages/VideoList';
import { VideoEditor } from './pages/VideoEditor';
import { VideoPlayer } from './pages/VideoPlayer';
import { Search } from './pages/Search';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="text-2xl font-bold text-primary-600">
                  АРХИВ
                </Link>
                <div className="hidden md:flex md:ml-8 md:space-x-8">
                  <Link
                    to="/"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Главная
                  </Link>
                  <Link
                    to="/videos"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Видео
                  </Link>
                  <Link
                    to="/search"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Поиск
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/videos" element={<VideoList />} />
            <Route path="/videos/:id/edit" element={<VideoEditor />} />
            <Route path="/videos/:id" element={<VideoPlayer />} />
            <Route path="/search" element={<Search />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
