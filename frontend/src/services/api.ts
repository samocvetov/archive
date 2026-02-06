import axios from 'axios';
import type {
  Video,
  VideoWithTags,
  Fragment,
  FragmentWithTags,
  Tag,
  TagWithCount,
  VideoCreate,
  FragmentCreate,
  FragmentUpdate,
  SearchQuery,
} from '../types';

const API_BASE_URL = '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videoApi = {
  upload: async (formData: FormData) => {
    const response = await api.post<Video>('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getAll: async (params?: {
    skip?: number;
    limit?: number;
    category?: string;
    subcategory?: string;
  }) => {
    const response = await api.get<Video[]>('/videos/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<VideoWithTags>(`/videos/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<VideoCreate>) => {
    const response = await api.put<Video>(`/videos/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/videos/${id}`);
    return response.data;
  },

  deleteSource: async (id: number, force: boolean = true) => {
    const response = await api.delete(`/videos/${id}/source`, {
      params: force ? { force: true } : undefined
    });
    return response.data;
  },

  search: async (query: SearchQuery) => {
    const response = await api.post<VideoWithTags[]>('/videos/search', query);
    return response.data;
  },
};

export const fragmentApi = {
  create: async (videoId: number, data: FragmentCreate) => {
    const response = await api.post<FragmentWithTags>(`/videos/${videoId}/fragments/`, data);
    return response.data;
  },

  getAll: async (videoId: number, query?: string) => {
    const response = await api.get<FragmentWithTags[]>(`/videos/${videoId}/fragments/`, {
      params: query ? { query } : undefined
    });
    return response.data;
  },

  search: async (query: string) => {
    const response = await api.get<FragmentWithTags[]>(`/fragments/search`, {
      params: { query }
    });
    return response.data;
  },

  getById: async (videoId: number, fragmentId: number) => {
    const response = await api.get<FragmentWithTags>(`/videos/${videoId}/fragments/${fragmentId}`);
    return response.data;
  },

  update: async (videoId: number, fragmentId: number, data: FragmentUpdate) => {
    const response = await api.put<Fragment>(`/videos/${videoId}/fragments/${fragmentId}`, data);
    return response.data;
  },

  delete: async (videoId: number, fragmentId: number) => {
    const response = await api.delete(`/videos/${videoId}/fragments/${fragmentId}`);
    return response.data;
  },
};

export const tagApi = {
  create: async (name: string) => {
    const response = await api.post<Tag>('/tags/', { name });
    return response.data;
  },

  getAll: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }) => {
    const response = await api.get<Tag[]>('/tags/', { params });
    return response.data;
  },

  getPopular: async (limit: number = 20) => {
    const response = await api.get<TagWithCount[]>('/tags/popular', { params: { limit } });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Tag>(`/tags/${id}`);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/tags/${id}`);
    return response.data;
  },
};
