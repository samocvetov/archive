import { useState, ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Upload, Video, Search, FolderOpen } from 'lucide-react';
import { videoApi } from '../services/api';

export function Home() {
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [tags, setTags] = useState('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', title);
    formData.append('category', category);
    formData.append('subcategory', subcategory);
    formData.append('tags', tags);

    try {
      await videoApi.upload(formData);
      setSelectedFile(null);
      setTitle('');
      setCategory('');
      setSubcategory('');
      setTags('');
      alert('Видео успешно загружено!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Ошибка при загрузке видео');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Добро пожаловать в АРХИВ
        </h1>
        <p className="text-lg text-gray-600">
          Управляйте видео архивом: загружайте, отмечайте фрагменты и добавляйте хештеги
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/videos"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <Video className="h-12 w-12 text-primary-500 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Все видео</h3>
          <p className="text-gray-600">Просмотр и управление загруженными видео</p>
        </Link>

        <Link
          to="/search"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <Search className="h-12 w-12 text-primary-500 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Поиск</h3>
          <p className="text-gray-600">Ищите видео по хештегам, категории и дате</p>
        </Link>

        <Link
          to="/videos/new"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <Upload className="h-12 w-12 text-primary-500 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Загрузить</h3>
          <p className="text-gray-600">Добавьте новые видео в архив</p>
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
          <Upload className="h-6 w-6 mr-2 text-primary-500" />
          Загрузить видео
        </h2>

        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Выберите видеофайл
            </label>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Название
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Хештеги (через запятую)
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="например: производство, носки, паша"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <button
            type="submit"
            disabled={uploading || !selectedFile}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 transition-colors"
          >
            {uploading ? 'Загрузка...' : 'Загрузить видео'}
          </button>
        </form>
      </div>
    </div>
  );
}
