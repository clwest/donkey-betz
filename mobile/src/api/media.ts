import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface MediaItem {
  id: string;
  type: 'image' | 'video';
  thumbnailUrl: string | null;
  fullUrl: string | null;
  prompt: string;
  model: string;
  createdAt: string;
  isFavorite: boolean;
  width?: number;
  height?: number;
  duration?: number;
}

interface RawImageItem {
  id: string;
  url?: string;
  thumbnail_url?: string;
  file_path?: string;
  cloudinary_url?: string;
  prompt?: string;
  model?: string;
  model_used?: string;
  image_type?: string;
  created_at?: string;
  is_favorite?: boolean;
  width?: number;
  height?: number;
}

interface RawVideoItem {
  id: string;
  video_url?: string;
  thumbnail_url?: string;
  prompt?: string;
  model?: string;
  model_used?: string;
  video_type?: string;
  created_at?: string;
  is_favorite?: boolean;
  duration?: number;
  status?: string;
}

// ── Normalizers ──────────────────────────────────────────────────────────────

function normalizeImage(raw: RawImageItem): MediaItem {
  const url = raw.url || raw.cloudinary_url || raw.file_path || null;
  return {
    id: raw.id,
    type: 'image',
    thumbnailUrl: raw.thumbnail_url || url,
    fullUrl: url,
    prompt: raw.prompt ?? '',
    model: raw.model_used || raw.model || '',
    createdAt: raw.created_at ?? '',
    isFavorite: raw.is_favorite ?? false,
    width: raw.width,
    height: raw.height,
  };
}

function normalizeVideo(raw: RawVideoItem): MediaItem {
  return {
    id: raw.id,
    type: 'video',
    thumbnailUrl: raw.thumbnail_url ?? null,
    fullUrl: raw.video_url ?? null,
    prompt: raw.prompt ?? '',
    model: raw.model_used || raw.model || '',
    createdAt: raw.created_at ?? '',
    isFavorite: raw.is_favorite ?? false,
    duration: raw.duration,
  };
}

// ── API calls ────────────────────────────────────────────────────────────────

export async function getImageHistory(params?: {
  limit?: number;
  offset?: number;
  image_type?: string;
}): Promise<{ items: MediaItem[]; total: number }> {
  const { data } = await http.get<{
    results?: RawImageItem[];
    images?: RawImageItem[];
    count?: number;
    total?: number;
  }>('/images/history/', { params });

  const raw = data.results ?? data.images ?? [];
  return {
    items: raw.map(normalizeImage),
    total: data.count ?? data.total ?? raw.length,
  };
}

export async function getVideoHistory(params?: {
  limit?: number;
  offset?: number;
  type?: string;
}): Promise<{ items: MediaItem[]; total: number }> {
  const { data } = await http.get<{
    results?: RawVideoItem[];
    videos?: RawVideoItem[];
    count?: number;
    total?: number;
    total_count?: number;
  }>('/v1/video/history/', { params });

  const raw = data.results ?? data.videos ?? [];
  return {
    items: raw.map(normalizeVideo),
    total: data.total_count ?? data.count ?? data.total ?? raw.length,
  };
}

export async function getAllMedia(params?: {
  limit?: number;
  offset?: number;
  type?: 'image' | 'video';
}): Promise<{ items: MediaItem[]; total: number }> {
  const limit = params?.limit ?? 30;
  const perType = Math.ceil(limit / 2);

  if (params?.type === 'image') {
    return getImageHistory({ limit, offset: params?.offset });
  }
  if (params?.type === 'video') {
    return getVideoHistory({ limit, offset: params?.offset });
  }

  const [images, videos] = await Promise.all([
    getImageHistory({ limit: perType, offset: params?.offset }),
    getVideoHistory({ limit: perType, offset: params?.offset }),
  ]);

  const merged = [...images.items, ...videos.items].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  );

  return { items: merged, total: images.total + videos.total };
}
