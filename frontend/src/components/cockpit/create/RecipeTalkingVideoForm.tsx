export interface TalkingVideoFormData {
  script: string
  voice: string
  mode: string
  sync_mode: string
  lipsync_model: string
  image_url: string
  color_grade: string
}

interface RecipeTalkingVideoFormProps {
  onChange: (data: TalkingVideoFormData) => void
  data: TalkingVideoFormData
}

const VOICE_OPTIONS = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
const MODE_OPTIONS = ['loop', 'multi_clip']
const SYNC_OPTIONS = ['cut_off', 'loop', 'pad']
const LIPSYNC_OPTIONS = ['latentsync', 'auto']
const GRADE_OPTIONS = ['', 'cinematic_warm', 'cinematic_cool', 'film_noir', 'vintage', 'vibrant']

export default function RecipeTalkingVideoForm({ onChange, data }: RecipeTalkingVideoFormProps) {
  const update = (field: keyof TalkingVideoFormData, value: string) => {
    onChange({ ...data, [field]: value })
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1">Script *</label>
        <textarea
          value={data.script}
          onChange={(e) => update('script', e.target.value)}
          placeholder="What should the character say?"
          rows={3}
          className="input w-full"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Voice</label>
          <select
            value={data.voice}
            onChange={(e) => update('voice', e.target.value)}
            className="input w-full text-sm"
          >
            {VOICE_OPTIONS.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Mode</label>
          <select
            value={data.mode}
            onChange={(e) => update('mode', e.target.value)}
            className="input w-full text-sm"
          >
            {MODE_OPTIONS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Sync Mode</label>
          <select
            value={data.sync_mode}
            onChange={(e) => update('sync_mode', e.target.value)}
            className="input w-full text-sm"
          >
            {SYNC_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Lipsync Model</label>
          <select
            value={data.lipsync_model}
            onChange={(e) => update('lipsync_model', e.target.value)}
            className="input w-full text-sm"
          >
            {LIPSYNC_OPTIONS.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1">Image URL (optional)</label>
        <input
          type="text"
          value={data.image_url}
          onChange={(e) => update('image_url', e.target.value)}
          placeholder="https://... character portrait"
          className="input w-full"
        />
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1">Color Grade</label>
        <select
          value={data.color_grade}
          onChange={(e) => update('color_grade', e.target.value)}
          className="input w-full text-sm"
        >
          {GRADE_OPTIONS.map((g) => (
            <option key={g} value={g}>{g || 'None'}</option>
          ))}
        </select>
      </div>
    </div>
  )
}
