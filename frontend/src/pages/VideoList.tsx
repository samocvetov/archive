import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Video as VideoType } from '../types';
import { videoApi } from '../services/api';
import { Clock, Calendar, FolderOpen, Trash2, Edit } from 'lucide-react';

export function VideoList() {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const data = await videoApi.getAll();
      setVideos(data);
    } catch (error) {
      console.error('Error loading videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить это видео?')) return;

    try {
      await videoApi.delete(id);
      setVideos(videos.filter((v) => v.id !== id));
    } catch (error) {
      console.error('Error deleting video:', error);
      alert('Ошибка при удалении видео');
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Все видео</h1>
        <Link
          to="/"
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
        >
          Загрузить новое видео
        </Link>
      </div>

      {videos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Видео не найдены</p>
          <Link to="/" className="text-primary-600 hover:underline mt-4 inline-block">
            Загрузите первое видео
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id}
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
                <h3 className="font-semibold text-lg mb-2 truncate" title={video.title || video.original_filename}>
                  {video.title || video.original_filename}
                </h3>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>{formatDuration(video.duration)}</span>
                  </div>
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>{formatDate(video.created_at)}</span>
                  </div>
                  {video.category && (
                    <div className="flex items-center">
                      <FolderOpen className="h-4 w-4 mr-2" />
                      <span>{video.category}</span>
                      {video.subcategory && <span className="ml-1">/ {video.subcategory}</span>}
                    </div>
                  )}
                </div>

                <div className="mt-4 flex space-x-2">
                  <Link
                    to={`/videos/${video.id}`}
                    className="flex-1 bg-primary-100 text-primary-700 py-2 px-3 rounded-md text-center hover:bg-primary-200 transition-colors"
                  >
                    Смотреть
                  </Link>
                  <Link
                    to={`/videos/${video.id}/edit`}
                    className="bg-gray-100 text-gray-700 py-2 px-3 rounded-md hover:bg-gray-200 transition-colors"
                    title="Редактировать"
                  >
                    <Edit className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(video.id)}
                    className="bg-red-100 text-red-700 py-2 px-3 rounded-md hover:bg-red-200 transition-colors"
                    title="Удалить"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
