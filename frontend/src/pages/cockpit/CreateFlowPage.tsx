import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import CreateStepper from '@/components/cockpit/create/CreateStepper'
import RecipeBlogForm, { type BlogFormData } from '@/components/cockpit/create/RecipeBlogForm'
import RecipeTalkingVideoForm, { type TalkingVideoFormData } from '@/components/cockpit/create/RecipeTalkingVideoForm'
import { RECIPES, type RecipeId } from '@/components/cockpit/create/recipes'
import { useJobStatus } from '@/hooks/cockpitQueries'
import { createBlog, createTalkingVideo } from '@/lib/cockpitApi'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import { ArrowLeft, Loader2, CheckCircle, XCircle } from 'lucide-react'

const DEFAULT_BLOG: BlogFormData = { topic: '', style: 'engaging', length: 'medium', citations: true }
const DEFAULT_VIDEO: TalkingVideoFormData = {
  script: '', voice: 'alloy', mode: 'loop', sync_mode: 'cut_off',
  lipsync_model: 'latentsync', image_url: '', color_grade: '',
}

export default function CockpitCreateFlowPage() {
  const { recipeId } = useParams<{ recipeId: string }>()
  const navigate = useNavigate()
  const recipe = RECIPES.find((r) => r.id === recipeId)

  const [step, setStep] = useState(0) // 0=Inputs, 1=Review, 2=Run
  const [blogData, setBlogData] = useState<BlogFormData>(DEFAULT_BLOG)
  const [videoData, setVideoData] = useState<TalkingVideoFormData>(DEFAULT_VIDEO)
  const [jobId, setJobId] = useState<string>()

  const { data: jobStatus } = useJobStatus(jobId)

  const blogMutation = useMutation({
    mutationFn: createBlog,
    onSuccess: (res) => {
      setJobId(res.run_id || res.job_id)
      setStep(2)
    },
  })

  const videoMutation = useMutation({
    mutationFn: createTalkingVideo,
    onSuccess: (res) => {
      setJobId(res.run_id || res.job_id)
      setStep(2)
    },
  })

  const mutation = recipeId === 'blog' ? blogMutation : videoMutation
  const isValid = recipeId === 'blog' ? blogData.topic.trim().length > 0 : videoData.script.trim().length > 0

  const handleRun = () => {
    if (recipeId === 'blog') {
      blogMutation.mutate(blogData)
    } else {
      videoMutation.mutate(videoData)
    }
  }

  if (!recipe) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate('/cockpit/create')} className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200">
          <ArrowLeft size={16} /> Back
        </button>
        <div className="card p-6 text-center text-gray-400">Unknown recipe: {recipeId}</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <button
        onClick={() => step === 0 ? navigate('/cockpit/create') : setStep(step - 1)}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ArrowLeft size={16} />
        {step === 0 ? 'Back to recipes' : 'Back'}
      </button>

      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">{recipe.title}</h1>
        <CreateStepper current={step} />
      </div>

      {/* Step 0: Inputs */}
      {step === 0 && (
        <div className="card p-5 space-y-5">
          {recipeId === 'blog' ? (
            <RecipeBlogForm data={blogData} onChange={setBlogData} />
          ) : (
            <RecipeTalkingVideoForm data={videoData} onChange={setVideoData} />
          )}
          <div className="flex justify-end">
            <button
              onClick={() => setStep(1)}
              disabled={!isValid}
              className="btn btn-primary disabled:opacity-40"
            >
              Review
            </button>
          </div>
        </div>
      )}

      {/* Step 1: Review */}
      {step === 1 && (
        <div className="card p-5 space-y-4">
          <h2 className="text-sm font-medium text-gray-400">Review your inputs</h2>
          <pre className="text-xs text-gray-300 bg-dark-bg rounded-lg p-4 overflow-auto max-h-64 font-mono">
            {JSON.stringify(recipeId === 'blog' ? blogData : videoData, null, 2)}
          </pre>
          {mutation.error && (
            <div className="text-sm text-red-400">
              Error: {(mutation.error as Error).message}
            </div>
          )}
          <div className="flex justify-end gap-3">
            <button onClick={() => setStep(0)} className="btn text-gray-400 hover:text-white">
              Edit
            </button>
            <button
              onClick={handleRun}
              disabled={mutation.isPending}
              className="btn btn-primary disabled:opacity-60 flex items-center gap-2"
            >
              {mutation.isPending && <Loader2 size={14} className="animate-spin" />}
              {mutation.isPending ? 'Submitting...' : 'Run'}
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Run status */}
      {step === 2 && (
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-3">
            {jobStatus?.status === 'completed' ? (
              <CheckCircle size={20} className="text-emerald-400" />
            ) : jobStatus?.status === 'failed' ? (
              <XCircle size={20} className="text-red-400" />
            ) : (
              <Loader2 size={20} className="text-primary-400 animate-spin" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-200">
                {jobStatus?.status === 'completed' ? 'Done!' : jobStatus?.status === 'failed' ? 'Failed' : 'Running...'}
              </p>
              <p className="text-xs text-gray-500">Job: {jobId?.slice(0, 12)}</p>
            </div>
            {jobStatus && (
              <StatusPill
                label={jobStatus.status}
                tone={
                  jobStatus.status === 'completed' ? 'green'
                    : jobStatus.status === 'failed' ? 'red'
                    : jobStatus.status === 'queued' ? 'gray'
                    : 'blue'
                }
              />
            )}
          </div>

          {jobStatus?.error && (
            <pre className="text-xs text-red-300 bg-dark-bg rounded-lg p-3 font-mono whitespace-pre-wrap">
              {jobStatus.error}
            </pre>
          )}

          {jobStatus?.progress != null && jobStatus.status !== 'completed' && jobStatus.status !== 'failed' && (
            <div className="w-full bg-dark-border rounded-full h-1.5">
              <div
                className="bg-primary-500 h-1.5 rounded-full transition-all"
                style={{ width: `${Math.round(jobStatus.progress * 100)}%` }}
              />
            </div>
          )}

          <div className="flex gap-3">
            {jobId && (
              <button
                onClick={() => navigate(`/cockpit/runs/${jobId}`)}
                className="btn btn-primary text-sm"
              >
                View Run Detail
              </button>
            )}
            <button
              onClick={() => { setStep(0); setJobId(undefined) }}
              className="btn text-sm text-gray-400 hover:text-white"
            >
              Create Another
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
