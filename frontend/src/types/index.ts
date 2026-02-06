export interface Video {
  id: number;
  filename: string;
  original_filename: string;
  title?: string;
  duration?: number;
  filepath?: string;
  file_size: number;
  mime_type: string;
  category?: string;
  subcategory?: string;
  created_at: string;
  updated_at: string;
}

export interface VideoWithTags extends Video {
  tags: Tag[];
  fragments: Fragment[];
}

export interface Fragment {
  id: number;
  video_id: number;
  name: string;
  description?: string;
  start_time: number;
  end_time: number;
  filepath?: string;  // Path to preview/thumbnail
  file_size?: number;
  video_filepath?: string;  // Path to fragment video file
  video_file_size?: number;
  created_at: string;
  tags?: Tag[];  // Optional tags for flexibility
  video?: Video; // Optional video reference
}

export interface FragmentWithTags extends Fragment {
  tags: Tag[];
  video: Video;
}

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

export interface TagWithCount extends Tag {
  count: number;
}

export interface VideoCreate {
  title?: string;
  category?: string;
  subcategory?: string;
}

export interface FragmentCreate {
  name: string;
  description?: string;
  start_time: number;
  end_time: number;
  tag_ids?: number[];
}

export interface FragmentUpdate {
  name?: string;
  description?: string;
  start_time?: number;
  end_time?: number;
  tag_ids?: number[];
}

export interface SearchQuery {
  query?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  date_from?: string;
  date_to?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
}
