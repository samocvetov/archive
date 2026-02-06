import { useEffect, useState, useRef, ChangeEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactPlayer from 'react-player';
import { VideoWithTags, FragmentWithTags, Tag } from '../types';
import { videoApi, fragmentApi, tagApi } from '../services/api';
import { Plus, Trash2, X, Tag as TagIcon } from 'lucide-react';

export function VideoEditor() {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<VideoWithTags | null>(null);
  const [fragments, setFragments] = useState<FragmentWithTags[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  
  const playerRef = useRef<ReactPlayer>(null);
  
  const [newFragment, setNewFragment] = useState({
    name: '',
    description: '',
    start_time: 0,
    end_time: 0,
    tag_ids: [] as number[],
  });
  
  const [currentTime, setCurrentTime] = useState(0);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedFragment, setSelectedFragment] = useState<FragmentWithTags | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handlePlayFragment = (fragment: FragmentWithTags) => {
    setSelectedFragment(fragment);
  };

  const handleBackToSource = () => {
    setSelectedFragment(null);
  };

  // Filter fragments based on search query
  const filteredFragments = searchQuery
    ? fragments.filter(fragment => 
        fragment.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        fragment.description?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : fragments;

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    try {
      const [videoData, fragmentsData, tagsData] = await Promise.all([
        videoApi.getById(parseInt(id)),
        fragmentApi.getAll(parseInt(id)),
        tagApi.getAll({ limit: 100 }),
      ]);
      setVideo(videoData);
      setFragments(fragmentsData);
      setAllTags(tagsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetStart = () => {
    setNewFragment({ ...newFragment, start_time: currentTime });
  };

  const handleSetEnd = () => {
    setNewFragment({ ...newFragment, end_time: currentTime });
  };

  const handleCreateFragment = async (e: ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!id || !newFragment.name) return;

    setIsCreating(true);
    try {
      const created = await fragmentApi.create(parseInt(id), newFragment);
      setFragments([...fragments, created]);
      setNewFragment({
        name: '',
        description: '',
        start_time: 0,
        end_time: 0,
        tag_ids: [],
      });
    } catch (error) {
      console.error('Error creating fragment:', error);
      alert('Ошибка при создании фрагмента');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteFragment = async (fragmentId: number) => {
    if (!confirm('Удалить этот фрагмент?')) return;
    if (!id) return;

    try {
      await fragmentApi.delete(parseInt(id), fragmentId);
      setFragments(fragments.filter((f) => f.id !== fragmentId));
    } catch (error) {
      console.error('Error deleting fragment:', error);
      alert('Ошибка при удалении фрагмента');
    }
  };

  const handleDeleteSourceVideo = async () => {
    if (!confirm('Удалить исходное видео? Фрагменты останутся в архиве.')) return;
    if (!id) return;

    try {
      // Останавливаем плеер перед удалением файла
      if (playerRef.current) {
        playerRef.current.getInternalPlayer()?.pause?.();
      }
      // Ждем немного чтобы файл освободился
      await new Promise(resolve => setTimeout(resolve, 500));
      
      await videoApi.deleteSource(parseInt(id));
      alert('Исходное видео удалено. Фрагменты сохранены в архиве.');
      loadData();
    } catch (error) {
      console.error('Error deleting source video:', error);
      alert('Ошибка при удалении исходного видео. Закройте плеер и попробуйте снова.');
    }
  };

  const handleAddTag = (tagId: number) => {
    if (!newFragment.tag_ids.includes(tagId)) {
      setNewFragment({
        ...newFragment,
        tag_ids: [...newFragment.tag_ids, tagId],
      });
    }
  };

  const handleRemoveTag = (tagId: number) => {
    setNewFragment({
      ...newFragment,
      tag_ids: newFragment.tag_ids.filter((id) => id !== tagId),
    });
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading || !video) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const selectedTags = allTags.filter((tag) => newFragment.tag_ids.includes(tag.id));
  const availableTags = allTags.filter((tag) => !newFragment.tag_ids.includes(tag.id));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{video.title || video.original_filename}</h1>
          <p className="text-gray-600 mt-1">
            Длительность: {formatTime(video.duration || 0)}
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleDeleteSourceVideo}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
          >
            Удалить исходное видео
          </button>
          <Link
            to={`/videos/${id}`}
            className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Вернуться к просмотру
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          {selectedFragment ? (
            <div>
              <div className="bg-black rounded-lg overflow-hidden aspect-video">
                <ReactPlayer
                  url={`/static/${selectedFragment.video_filepath}`}
                  width="100%"
                  height="100%"
                  controls
                  playing
                />
              </div>
              <div className="mt-2 flex items-center justify-between">
                <h3 className="font-semibold">{selectedFragment.name}</h3>
                <button
                  onClick={handleBackToSource}
                  className="text-sm text-primary-600 hover:text-primary-800"
                >
                  {video.filepath ? 'Назад к исходному видео' : 'Закрыть фрагмент'}
                </button>
              </div>
            </div>
          ) : video.filepath ? (
            <div className="bg-black rounded-lg overflow-hidden aspect-video">
              <ReactPlayer
                ref={playerRef}
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
                  Фрагменты ({fragments?.length || 0}) сохранены в архиве
                </p>
              </div>
            </div>
          )}

          {video.filepath && (
            <div className="mt-4 bg-white rounded-lg shadow-md p-4">
              <h3 className="font-semibold mb-3">Создать фрагмент</h3>
              <form onSubmit={handleCreateFragment} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Название фрагмента
                </label>
                <input
                  type="text"
                  value={newFragment.name}
                  onChange={(e) => setNewFragment({ ...newFragment, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Описание
                </label>
                <textarea
                  value={newFragment.description}
                  onChange={(e) => setNewFragment({ ...newFragment, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Начало: {formatTime(newFragment.start_time)}
                  </label>
                  <button
                    type="button"
                    onClick={handleSetStart}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors"
                  >
                    Установить текущее
                  </button>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Конец: {formatTime(newFragment.end_time)}
                  </label>
                  <button
                    type="button"
                    onClick={handleSetEnd}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors"
                  >
                    Установить текущее
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Хештеги
                </label>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {selectedTags.map((tag) => (
                      <span
                        key={tag.id}
                        className="inline-flex items-center bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm"
                      >
                        <TagIcon className="h-3 w-3 mr-1" />
                        {tag.name}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag.id)}
                          className="ml-2 hover:text-primary-900"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  {availableTags.length > 0 && (
                    <select
                      value=""
                      onChange={(e) => e.target.value && handleAddTag(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">Добавить хештег...</option>
                      {availableTags.map((tag) => (
                        <option key={tag.id} value={tag.id}>
                          {tag.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              </div>

              <button
                type="submit"
                disabled={isCreating || !newFragment.name}
                className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 transition-colors"
              >
                {isCreating ? 'Создание...' : 'Создать фрагмент'}
              </button>
            </form>
          </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="font-semibold mb-3">Фрагменты ({filteredFragments?.length || 0})</h3>
          
          {/* Search input */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Поиск фрагментов..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          {!filteredFragments || filteredFragments.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              {searchQuery ? 'Ничего не найдено' : 'Нет фрагментов'}
            </p>
          ) : (
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {filteredFragments.map((fragment) => (
                <div
                  key={fragment.id}
                  className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium">{fragment.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {formatTime(fragment.start_time)} - {formatTime(fragment.end_time)}
                      </p>
                      {fragment.description && (
                        <p className="text-sm text-gray-500 mt-1">{fragment.description}</p>
                      )}
                      {fragment.tags?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
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
                    </div>
                    <button
                      onClick={() => handleDeleteFragment(fragment.id)}
                      className="text-red-600 hover:text-red-800 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  {video.filepath ? (
                    <button
                      onClick={() => playerRef.current?.seekTo(fragment.start_time)}
                      className="mt-2 text-sm text-primary-600 hover:text-primary-800"
                    >
                      Перейти к фрагменту
                    </button>
                  ) : fragment.video_filepath ? (
                    <button
                      onClick={() => handlePlayFragment(fragment)}
                      className="mt-2 text-sm text-primary-600 hover:text-primary-800"
                    >
                      Воспроизвести фрагмент
                    </button>
                  ) : (
                    <p className="mt-2 text-sm text-gray-400">Видеофайл фрагмента не найден</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
