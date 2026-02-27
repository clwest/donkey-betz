export type RecipeId = 'blog' | 'talking-video'

export interface CockpitRecipe {
  id: RecipeId
  title: string
  description: string
  eta: string
  tags: string[]
}

export const RECIPES: CockpitRecipe[] = [
  {
    id: 'blog',
    title: 'Blog Post',
    description: 'Generate a researched blog post through the deliberation pipeline with multi-agent review.',
    eta: '1-3 min',
    tags: ['deliberation', 'content'],
  },
  {
    id: 'talking-video',
    title: 'Talking Character Video',
    description: 'Create a lip-synced talking character video with TTS, motion, and optional color grading.',
    eta: '2-5 min',
    tags: ['video', 'TTS', 'lipsync'],
  },
]
