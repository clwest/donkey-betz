/**
 * Session 866: Career Tab - ATS Resume Optimizer
 *
 * Features:
 * - Paste resume and job description
 * - Real-time ATS score with category breakdown
 * - Missing keywords highlighted
 * - Optimization suggestions
 * - Generate ATS-optimized summary
 */

import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  FileText, Target, Sparkles, AlertCircle, CheckCircle2,
  TrendingUp, Loader2, Copy, RefreshCw, Briefcase,
  ChevronDown, ChevronRight, Lightbulb, Zap
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface CategoryScore {
  score: number
  matched: string[]
  missing: string[]
  job_required: string[]
  resume_has: string[]
}

interface ATSAnalysisResult {
  success: boolean
  overall_score: number
  match_level: 'excellent' | 'good' | 'moderate' | 'low' | 'poor'
  category_scores: Record<string, CategoryScore>
  missing_keywords: string[]
  detected_industry?: string
  suggestions?: {
    priority_keywords_to_add: Array<{
      keyword: string
      priority: 'high' | 'medium'
      reason: string
    }>
    keyword_placement_tips: string[]
    action_verb_suggestions: string[]
    overall_recommendations: string[]
  }
  error?: string
}

interface GenerateSummaryResult {
  success: boolean
  summary: string
  style: string
  error?: string
}

// API functions
async function analyzeResume(data: {
  resume_text: string
  job_description: string
  include_suggestions: boolean
}): Promise<ATSAnalysisResult> {
  const response = await fetch('/api/ats/analyze/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data)
  })
  return response.json()
}

async function generateSummary(data: {
  job_description: string
  style: string
}): Promise<GenerateSummaryResult> {
  const response = await fetch('/api/ats/generate-summary/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data)
  })
  return response.json()
}

// Score color helper
function getScoreColor(score: number): string {
  if (score >= 85) return 'text-green-400'
  if (score >= 70) return 'text-emerald-400'
  if (score >= 50) return 'text-yellow-400'
  if (score >= 30) return 'text-orange-400'
  return 'text-red-400'
}

function getScoreBgColor(score: number): string {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-emerald-500'
  if (score >= 50) return 'bg-yellow-500'
  if (score >= 30) return 'bg-orange-500'
  return 'bg-red-500'
}

function getMatchLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    excellent: 'Excellent Match',
    good: 'Good Match',
    moderate: 'Moderate Match',
    low: 'Low Match',
    poor: 'Poor Match'
  }
  return labels[level] || level
}

export function CareerTab() {
  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [analysisResult, setAnalysisResult] = useState<ATSAnalysisResult | null>(null)
  const [generatedSummary, setGeneratedSummary] = useState<string | null>(null)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [summaryStyle, setSummaryStyle] = useState<'professional' | 'creative' | 'technical'>('professional')

  const analyzeMutation = useMutation({
    mutationFn: analyzeResume,
    onSuccess: (data) => {
      setAnalysisResult(data)
      // Auto-expand categories with issues
      const toExpand = new Set<string>()
      if (data.category_scores) {
        Object.entries(data.category_scores).forEach(([cat, score]) => {
          if (typeof score === 'object' && score.score < 70) {
            toExpand.add(cat)
          }
        })
      }
      setExpandedCategories(toExpand)
    }
  })

  const summaryMutation = useMutation({
    mutationFn: generateSummary,
    onSuccess: (data) => {
      if (data.success) {
        setGeneratedSummary(data.summary)
      }
    }
  })

  const handleAnalyze = () => {
    if (!resumeText.trim() || !jobDescription.trim()) return
    analyzeMutation.mutate({
      resume_text: resumeText,
      job_description: jobDescription,
      include_suggestions: true
    })
  }

  const handleGenerateSummary = () => {
    if (!jobDescription.trim()) return
    summaryMutation.mutate({
      job_description: jobDescription,
      style: summaryStyle
    })
  }

  const toggleCategory = (cat: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(cat)) {
      newExpanded.delete(cat)
    } else {
      newExpanded.add(cat)
    }
    setExpandedCategories(newExpanded)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="h-full flex flex-col bg-dark-bg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary-500/20">
            <Briefcase className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">ATS Resume Optimizer</h2>
            <p className="text-sm text-gray-400">Optimize your resume for Applicant Tracking Systems</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Input */}
          <div className="space-y-4">
            {/* Resume Input */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-primary-400" />
                <h3 className="font-medium text-white">Your Resume</h3>
              </div>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here..."
                className="w-full h-48 bg-dark-bg border border-dark-border rounded-lg p-3 text-sm text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-primary-500"
              />
              <p className="text-xs text-gray-500 mt-2">
                {resumeText.length} characters
              </p>
            </div>

            {/* Job Description Input */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-4 h-4 text-accent-purple" />
                <h3 className="font-medium text-white">Job Description</h3>
              </div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the target job description here..."
                className="w-full h-48 bg-dark-bg border border-dark-border rounded-lg p-3 text-sm text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-primary-500"
              />
              <p className="text-xs text-gray-500 mt-2">
                {jobDescription.length} characters
              </p>
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={!resumeText.trim() || !jobDescription.trim() || analyzeMutation.isPending}
              className={cn(
                'w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors',
                resumeText.trim() && jobDescription.trim()
                  ? 'bg-primary-500 hover:bg-primary-600 text-white'
                  : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              )}
            >
              {analyzeMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Analyze ATS Compatibility
                </>
              )}
            </button>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-4">
            {analysisResult ? (
              <>
                {/* Score Card */}
                <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-white">ATS Score</h3>
                    {analysisResult.detected_industry && (
                      <span className="text-xs px-2 py-1 rounded bg-accent-purple/20 text-accent-purple">
                        {analysisResult.detected_industry}
                      </span>
                    )}
                  </div>

                  {/* Score Display */}
                  <div className="flex items-center gap-6 mb-6">
                    <div className="relative w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="8"
                          className="text-gray-700"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="8"
                          strokeDasharray={`${(analysisResult.overall_score / 100) * 251.2} 251.2`}
                          className={getScoreColor(analysisResult.overall_score)}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className={cn('text-2xl font-bold', getScoreColor(analysisResult.overall_score))}>
                          {Math.round(analysisResult.overall_score)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className={cn('text-lg font-semibold', getScoreColor(analysisResult.overall_score))}>
                        {getMatchLevelLabel(analysisResult.match_level)}
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        {analysisResult.overall_score >= 70
                          ? 'Your resume is well-optimized for this role'
                          : 'Consider adding missing keywords to improve your score'}
                      </p>
                    </div>
                  </div>

                  {/* Category Breakdown */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Category Breakdown</h4>
                    {Object.entries(analysisResult.category_scores).map(([category, data]) => {
                      const score = typeof data === 'object' ? data.score : 0
                      const isExpanded = expandedCategories.has(category)
                      const categoryData = data as CategoryScore

                      return (
                        <div key={category} className="bg-dark-bg rounded-lg overflow-hidden">
                          <button
                            onClick={() => toggleCategory(category)}
                            className="w-full p-3 flex items-center justify-between hover:bg-dark-border/50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              {isExpanded ? (
                                <ChevronDown className="w-4 h-4 text-gray-400" />
                              ) : (
                                <ChevronRight className="w-4 h-4 text-gray-400" />
                              )}
                              <span className="text-sm text-gray-300 capitalize">
                                {category.replace(/_/g, ' ')}
                              </span>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                  className={cn('h-full transition-all', getScoreBgColor(score))}
                                  style={{ width: `${score}%` }}
                                />
                              </div>
                              <span className={cn('text-sm font-medium w-12 text-right', getScoreColor(score))}>
                                {Math.round(score)}%
                              </span>
                            </div>
                          </button>

                          {isExpanded && categoryData.missing && categoryData.missing.length > 0 && (
                            <div className="px-3 pb-3 pt-1">
                              <p className="text-xs text-gray-500 mb-2">Missing keywords:</p>
                              <div className="flex flex-wrap gap-1">
                                {categoryData.missing.map((kw) => (
                                  <span
                                    key={kw}
                                    className="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400"
                                  >
                                    {kw}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Missing Keywords */}
                {analysisResult.missing_keywords && analysisResult.missing_keywords.length > 0 && (
                  <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <AlertCircle className="w-4 h-4 text-orange-400" />
                      <h3 className="font-medium text-white">Missing Keywords</h3>
                      <span className="text-xs px-2 py-0.5 rounded bg-orange-500/20 text-orange-400">
                        {analysisResult.missing_keywords.length}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.missing_keywords.map((kw) => (
                        <span
                          key={kw}
                          className="px-2 py-1 text-sm rounded-lg bg-orange-500/10 text-orange-300 border border-orange-500/30"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-3">
                      Add these keywords to your resume to improve ATS compatibility
                    </p>
                  </div>
                )}

                {/* Suggestions */}
                {analysisResult.suggestions && (
                  <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                      <h3 className="font-medium text-white">Optimization Tips</h3>
                    </div>
                    <div className="space-y-3">
                      {analysisResult.suggestions.keyword_placement_tips.map((tip, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm">
                          <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-300">{tip}</span>
                        </div>
                      ))}
                      {analysisResult.suggestions.overall_recommendations.map((rec, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm">
                          <TrendingUp className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-300">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Generate Summary */}
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-4 h-4 text-accent-cyan" />
                    <h3 className="font-medium text-white">Generate ATS Summary</h3>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">
                    Create an ATS-optimized professional summary tailored to this job
                  </p>
                  <div className="flex gap-2 mb-3">
                    {(['professional', 'creative', 'technical'] as const).map((style) => (
                      <button
                        key={style}
                        onClick={() => setSummaryStyle(style)}
                        className={cn(
                          'px-3 py-1.5 text-sm rounded-lg transition-colors capitalize',
                          summaryStyle === style
                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/50'
                            : 'bg-dark-bg text-gray-400 hover:text-gray-300'
                        )}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                  <button
                    onClick={handleGenerateSummary}
                    disabled={summaryMutation.isPending}
                    className="w-full py-2 rounded-lg bg-accent-cyan/20 text-accent-cyan hover:bg-accent-cyan/30 transition-colors flex items-center justify-center gap-2"
                  >
                    {summaryMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Generate Summary
                      </>
                    )}
                  </button>

                  {generatedSummary && (
                    <div className="mt-4 p-3 bg-dark-bg rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-gray-500">Generated Summary</span>
                        <button
                          onClick={() => copyToClipboard(generatedSummary)}
                          className="p-1 text-gray-400 hover:text-white transition-colors"
                          title="Copy to clipboard"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-300 leading-relaxed">{generatedSummary}</p>
                    </div>
                  )}
                </div>
              </>
            ) : (
              /* Empty State */
              <div className="bg-dark-card border border-dark-border rounded-xl p-8 flex flex-col items-center justify-center text-center">
                <div className="p-4 rounded-full bg-primary-500/10 mb-4">
                  <Target className="w-8 h-8 text-primary-400" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Ready to Optimize</h3>
                <p className="text-sm text-gray-400 max-w-sm">
                  Paste your resume and target job description, then click "Analyze" to see your ATS compatibility score and get optimization suggestions.
                </p>
                <div className="mt-6 grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-primary-400">85%+</p>
                    <p className="text-xs text-gray-500">Excellent</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-400">70%+</p>
                    <p className="text-xs text-gray-500">Good</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-yellow-400">50%+</p>
                    <p className="text-xs text-gray-500">Moderate</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CareerTab
