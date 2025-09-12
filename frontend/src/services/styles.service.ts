import { apiClient } from './api.config';
import { Logger } from '../utils/logger';

export interface VisualStyle {
  id: string;
  name: string;
  category: string;
  description: string;
  prompt: string;
  negative_prompt: string;
  tags: string[];
  use_cases: string[];
  cfg_scale: number;
  steps: number;
  emoji?: string;
  popular?: boolean;
}

export interface StyleCategory {
  id: string;
  name: string;
  description: string;
  styles: VisualStyle[];
}

class StylesService {
  private cachedStyles: VisualStyle[] | null = null;
  private cacheTime: number = 0;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  async getAllStyles(): Promise<VisualStyle[]> {
    // Check cache
    if (this.cachedStyles && Date.now() - this.cacheTime < this.CACHE_DURATION) {
      Logger.debug('StylesService', 'Returning cached styles', { count: this.cachedStyles.length });
      return this.cachedStyles;
    }

    try {
      Logger.api('GET', '/api/styles/');
      const response = await apiClient.get('/v1/styles/');
      
      // The backend returns an object with categories
      const data = response.data;
      let styles: VisualStyle[] = [];
      
      // Check if the response has a categories object
      if (data.categories && typeof data.categories === 'object') {
        // Iterate through each category
        Object.entries(data.categories).forEach(([categoryName, categoryStyles]: [string, any]) => {
          if (Array.isArray(categoryStyles)) {
            categoryStyles.forEach((style: any) => {
              styles.push({
                id: style.id || style.name,
                name: style.description || style.name || 'Unnamed Style',
                category: categoryName,
                description: style.description || style.preview_prompt || '',
                prompt: style.prompt || style.preview_prompt || '',
                negative_prompt: style.negative_prompt || '',
                tags: style.tags || [],
                use_cases: style.use_cases || [],
                cfg_scale: style.cfg_scale || 7,
                steps: style.steps || 30,
                emoji: this.getStyleEmoji(style.name || style.id),
                popular: false  // Will be set below
              });
            });
          }
        });
      } else if (Array.isArray(data)) {
        // Handle array format
        styles = data;
      } else if (typeof data === 'object') {
        // Handle flat object format
        styles = Object.entries(data).map(([key, value]: [string, any]) => ({
          id: key,
          name: value.name || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          category: value.category || 'General',
          description: value.description || value.name || '',
          prompt: value.prompt || '',
          negative_prompt: value.negative_prompt || value.negative || '',
          tags: value.tags || [],
          use_cases: value.use_cases || [],
          cfg_scale: value.cfg_scale || 7,
          steps: value.steps || 30,
          emoji: value.emoji,
          popular: value.popular || false
        }));
      }
      
      // Mark some popular styles
      const popularStyleIds = [
        'photorealistic',
        'cinematic_portrait',
        'digital_art_masterpiece',
        'anime_character',
        'cyberpunk_neon',
        'oil_painting_classical',
        'watercolor_dream',
        'sketch_notebook',
        'isometric_3d',
        'studio_portrait'
      ];
      
      styles.forEach(style => {
        if (popularStyleIds.includes(style.id)) {
          style.popular = true;
        }
      });
      
      this.cachedStyles = styles;
      this.cacheTime = Date.now();
      
      Logger.state('StylesService', 'Styles loaded', { count: styles.length });
      return styles;
    } catch (error) {
      Logger.error('StylesService.getAllStyles', error);
      
      // Return fallback styles if API fails
      return this.getFallbackStyles();
    }
  }

  async getStylesByCategory(): Promise<StyleCategory[]> {
    const styles = await this.getAllStyles();
    
    // Group styles by category
    const categoryMap = new Map<string, VisualStyle[]>();
    
    styles.forEach(style => {
      const category = style.category || 'General';
      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(style);
    });
    
    // Convert to array of categories
    const categories: StyleCategory[] = Array.from(categoryMap.entries()).map(([name, styles]) => ({
      id: name.toLowerCase().replace(/\s+/g, '_'),
      name,
      description: this.getCategoryDescription(name),
      styles: styles.sort((a, b) => {
        // Sort popular styles first
        if (a.popular && !b.popular) return -1;
        if (!a.popular && b.popular) return 1;
        return a.name.localeCompare(b.name);
      })
    }));
    
    return categories.sort((a, b) => a.name.localeCompare(b.name));
  }

  private getCategoryDescription(category: string): string {
    const descriptions: Record<string, string> = {
      'Professional': 'Business and corporate styles for presentations',
      'Creative': 'Artistic and creative styles for unique visuals',
      'Digital': 'Modern digital art and graphics styles',
      'Photography': 'Photography and realistic image styles',
      'Photo': 'Photography and realistic image styles',
      '3D': '3D rendering and animation styles',
      'Gaming': 'Video game and pixel art aesthetics',
      'Anime': 'Anime, manga, and Japanese art styles',
      'Retro': 'Vintage and nostalgic design styles',
      'Fantasy': 'Fantasy and magical art styles',
      'Animation': 'Animated and cartoon styles',
      'Art': 'Traditional and fine art styles',
      'Achievement': 'Badge and achievement graphics',
      'Modern': 'Contemporary and minimalist designs',
      'Urban': 'Street and urban art styles',
      'Illustration': 'Hand-drawn illustration styles'
    };
    
    return descriptions[category] || 'Various visual styles';
  }

  private getStyleEmoji(styleName: string): string {
    const emojiMap: Record<string, string> = {
      'corporate_minimal': '💼',
      'tech_startup': '🚀',
      'professional_presentation': '📊',
      'digital_art_masterpiece': '🎨',
      'watercolor_dream': '🌊',
      'sketch_notebook': '✏️',
      'cyberpunk_neon': '🌃',
      'synthwave_retro': '🌆',
      'glassmorphism_ui': '🔮',
      'cinematic_portrait': '🎬',
      'photorealistic': '📸',
      'oil_painting_classical': '🖼️',
      'anime_character': '🎌',
      'anime_background': '🏯',
      'manga_style': '📚',
      'comic_book': '💥',
      'pixel_art': '👾',
      'isometric_3d': '🎲',
      'studio_portrait': '📷',
      'architectural': '🏛️',
      'minimal_design': '⬜',
      'retro_vintage': '📻',
      'graffiti_street': '🎭',
      'game_concept': '🎮',
      'double_exposure': '👥',
      'fantasy_world': '🐉',
      'sci_fi_concept': '🛸',
      'dark_gothic': '🦇',
      'nature_landscape': '🌲',
      'food_photography': '🍔',
      'product_showcase': '📦',
      'fashion_editorial': '👗',
      'abstract_modern': '🔷',
      'minimalist': '⚪',
      'steampunk': '⚙️',
      'surreal': '🌀',
      'film_noir': '🎬',
      'studio_ghibli': '🌸',
      'horror': '👻',
      'achievement': '🏆',
      'badge': '🥇',
      'space': '🚀',
      'underwater': '🐠',
      'magical': '✨'
    };
    
    return emojiMap[styleName] || '🎨';
  }

  private getFallbackStyles(): VisualStyle[] {
    // Fallback styles if API is unavailable
    return [
      {
        id: 'photorealistic',
        name: 'Photorealistic',
        category: 'Photo',
        description: 'Ultra-realistic photography style',
        prompt: 'photorealistic, high quality, detailed',
        negative_prompt: 'cartoon, anime, illustration, painting',
        tags: ['photo', 'realistic'],
        use_cases: ['portraits', 'products'],
        cfg_scale: 7,
        steps: 30,
        popular: true
      },
      {
        id: 'digital_art',
        name: 'Digital Art',
        category: 'Digital',
        description: 'Modern digital artwork style',
        prompt: 'digital art, trending on artstation',
        negative_prompt: 'photo, realistic, blurry',
        tags: ['digital', 'art'],
        use_cases: ['illustrations', 'concept art'],
        cfg_scale: 7,
        steps: 30,
        popular: true
      },
      {
        id: 'oil_painting',
        name: 'Oil Painting',
        category: 'Creative',
        description: 'Classical oil painting style',
        prompt: 'oil painting, masterpiece, classical art',
        negative_prompt: 'photo, digital, modern',
        tags: ['painting', 'classical'],
        use_cases: ['art', 'portraits'],
        cfg_scale: 8,
        steps: 35
      },
      {
        id: 'anime',
        name: 'Anime',
        category: 'Anime',
        description: 'Japanese anime art style',
        prompt: 'anime style, manga, cel shaded',
        negative_prompt: 'realistic, photo, western',
        tags: ['anime', 'manga'],
        use_cases: ['characters', 'illustrations'],
        cfg_scale: 7,
        steps: 30,
        popular: true
      },
      {
        id: 'cyberpunk',
        name: 'Cyberpunk',
        category: 'Digital',
        description: 'Futuristic neon cyberpunk aesthetic',
        prompt: 'cyberpunk, neon lights, futuristic',
        negative_prompt: 'medieval, rustic, natural',
        tags: ['cyberpunk', 'futuristic'],
        use_cases: ['sci-fi', 'concept art'],
        cfg_scale: 7,
        steps: 30,
        popular: true
      },
      {
        id: 'watercolor',
        name: 'Watercolor',
        category: 'Creative',
        description: 'Soft watercolor painting style',
        prompt: 'watercolor painting, soft colors, artistic',
        negative_prompt: 'photo, digital, harsh',
        tags: ['watercolor', 'painting'],
        use_cases: ['art', 'illustrations'],
        cfg_scale: 6,
        steps: 25
      },
      {
        id: '3d_render',
        name: '3D Render',
        category: '3D',
        description: 'Professional 3D rendering',
        prompt: '3d render, octane render, unreal engine',
        negative_prompt: '2d, flat, drawing',
        tags: ['3d', 'render'],
        use_cases: ['3d models', 'visualization'],
        cfg_scale: 7,
        steps: 30
      },
      {
        id: 'sketch',
        name: 'Sketch',
        category: 'Creative',
        description: 'Hand-drawn pencil sketch',
        prompt: 'pencil sketch, hand drawn, artistic',
        negative_prompt: 'photo, color, digital',
        tags: ['sketch', 'drawing'],
        use_cases: ['concepts', 'drafts'],
        cfg_scale: 6,
        steps: 20
      }
    ];
  }
}

export const stylesService = new StylesService();