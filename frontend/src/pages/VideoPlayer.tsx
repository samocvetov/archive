import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactPlayer from 'react-player';
import { VideoWithTags, FragmentWithTags } from '../types';
import { videoApi, fragmentApi } from '../services/api';
import { Edit, Tag as TagIcon } from 'lucide-react';

export function VideoPlayer() {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<VideoWithTags | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    try {
      const videoData = await videoApi.getById(parseInt(id));
      setVideo(videoData);
    } catch (error) {
      console.error('Error loading video:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleJumpToFragment = (startTime: number) => {
    const player = document.querySelector('video');
    if (player) {
      player.currentTime = startTime;
    }
  };

  if (loading || !video) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{video.title || video.original_filename}</h1>
          <p className="text-gray-600 mt-1">
            Длительность: {formatTime(video.duration || 0)}
          </p>
        </div>
        <Link
          to={`/videos/${id}/edit`}
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors flex items-center"
        >
          <Edit className="h-4 w-4 mr-2" />
          Редактировать фрагменты
        </Link>
      </div>

      {video.filepath ? (
        <div className="bg-black rounded-lg overflow-hidden aspect-video">
          <ReactPlayer
            url={`/static/${video.filename}`}
            width="100%"
            height="100%"
            controls
            onProgress={(state) => setCurrentTime(state.playedSeconds)}
          />
        </div>
      ) : (
        <div className="bg-gray-100 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
          <div className="text-center p-8">
            <div className="text-6xl mb-4">🎬</div>
            <h3 className="font-semibold text-gray-700 mb-2">Исходное видео удалено</h3>
            <p className="text-gray-500 text-sm">
              {video.fragments?.length || 0} фрагментов сохранено в архиве
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">Информация</h3>
          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Дата создания:</span>{' '}
              {new Date(video.created_at).toLocaleDateString('ru-RU')}
            </div>
            <div>
              <span className="font-medium">Размер:</span>{' '}
              {(video.file_size / (1024 * 1024)).toFixed(2)} MB
            </div>
            {video.category && (
              <div>
                <span className="font-medium">Категория:</span> {video.category}
              </div>
            )}
            {video.subcategory && (
              <div>
                <span className="font-medium">Подкатегория:</span> {video.subcategory}
              </div>
            )}
          </div>
        </div>

        {video.tags && video.tags.length > 0 && (
          <div>
            <h3 className="font-semibold text-lg mb-2">Хештеги</h3>
            <div className="flex flex-wrap gap-2">
              {video.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="inline-flex items-center bg-primary-100 text-primary-700 px-3 py-1 rounded-full"
                >
                  <TagIcon className="h-4 w-4 mr-1" />
                  {tag.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {video.fragments && video.fragments.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="font-semibold text-lg mb-4">Фрагменты ({video.fragments.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {video.fragments.map((fragment) => (
              <div
                key={fragment.id}
                className={`border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors ${video.filepath ? 'cursor-pointer' : ''}`}
                onClick={() => video.filepath && handleJumpToFragment(fragment.start_time)}
              >
                <h4 className="font-medium mb-2">{fragment.name}</h4>
                <p className="text-sm text-gray-600 mb-2">
                  {formatTime(fragment.start_time)} - {formatTime(fragment.end_time)}
                </p>
                {fragment.description && (
                  <p className="text-sm text-gray-500 mb-2">{fragment.description}</p>
                )}
                {fragment.tags && fragment.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {fragment.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="inline-flex items-center bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full text-xs"
                      >
                        <TagIcon className="h-3 w-3 mr-1" />
                        {tag.name}
                      </span>
                    ))}
                  </div>
                )}
                {!video.filepath && fragment.video_filepath && (
                  <button
                    className="mt-2 text-sm text-primary-600 hover:text-primary-800"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(`/static/${fragment.video_filepath}`, '_blank');
                    }}
                  >
                    Воспроизвести фрагмент
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
