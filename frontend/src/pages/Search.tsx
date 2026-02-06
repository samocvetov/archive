import { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { VideoWithTags } from '../types';
import { videoApi } from '../services/api';
import { Search as SearchIcon, Calendar, Tag as TagIcon, Filter, X } from 'lucide-react';

export function Search() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [tags, setTags] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [results, setResults] = useState<VideoWithTags[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSearched(true);

    try {
      const searchParams: any = {};
      if (query) searchParams.query = query;
      if (category) searchParams.category = category;
      if (subcategory) searchParams.subcategory = subcategory;
      if (tags) searchParams.tags = tags.split(',').map((t) => t.trim().toLowerCase()).filter(Boolean);
      if (dateFrom) searchParams.date_from = dateFrom;
      if (dateTo) searchParams.date_to = dateTo;

      const data = await videoApi.search(searchParams);
      setResults(data);
    } catch (error) {
      console.error('Error searching:', error);
      alert('Ошибка при поиске');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setQuery('');
    setCategory('');
    setSubcategory('');
    setTags('');
    setDateFrom('');
    setDateTo('');
    setResults([]);
    setSearched(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Поиск видео</h1>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <SearchIcon className="h-4 w-4 mr-2" />
              Поисковый запрос
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Введите название или часть названия видео"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Категория
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Подкатегория
              </label>
              <input
                type="text"
                value={subcategory}
                onChange={(e) => setSubcategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <TagIcon className="h-4 w-4 mr-2" />
              Хештеги
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="через запятую, например: производство, носки"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                Дата с
              </label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                Дата до
              </label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 transition-colors flex items-center justify-center"
            >
              <SearchIcon className="h-4 w-4 mr-2" />
              {loading ? 'Поиск...' : 'Найти'}
            </button>
            {searched && (
              <button
                type="button"
                onClick={clearFilters}
                className="bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors flex items-center"
              >
                <X className="h-4 w-4 mr-2" />
                Сбросить
              </button>
            )}
          </div>
        </form>
      </div>

      {searched && (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Результаты поиска ({results.length})
          </h2>
          {results.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <p className="text-gray-500 text-lg">Видео не найдены</p>
              <p className="text-gray-400 mt-2">Попробуйте изменить параметры поиска</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((video) => (
                <Link
                  key={video.id}
                  to={`/videos/${video.id}`}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <div className="aspect-video bg-gray-200 flex items-center justify-center">
                    <img
                      src={`/static/thumbnails/${video.id}.jpg`}
                      alt={video.title || video.original_filename}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%239ca3af"%3E%3Cpath d="M8 5v14l11-7z"/%3E%3C/svg%3E';
                      }}
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold mb-2 truncate" title={video.title || video.original_filename}>
                      {video.title || video.original_filename}
                    </h3>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>{formatDate(video.created_at)}</span>
                      </div>
                      {video.category && (
                        <div>
                          Категория: {video.category}
                          {video.subcategory && ` / ${video.subcategory}`}
                        </div>
                      )}
                      {video.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {video.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag.id}
                              className="inline-flex items-center bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full text-xs"
                            >
                              <TagIcon className="h-3 w-3 mr-1" />
                              {tag.name}
                            </span>
                          ))}
                          {video.tags.length > 3 && (
                            <span className="text-gray-500 text-xs">
                              +{video.tags.length - 3} ещё
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
