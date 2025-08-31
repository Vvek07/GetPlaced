'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Upload, FileText, Target, BarChart3, Plus, Eye, AlertCircle, CheckCircle, Clock, TrendingUp, Award, Brain, Zap } from 'lucide-react'

interface Analysis {
  id: number
  ats_score: number
  strong_keywords: string[]
  missing_keywords: string[]
  suggestions: string[]
  job_title?: string
  created_at: string
  analysis_details?: {
    detailed_analysis: {
      keyword_density: number
      industry_alignment: number
      experience_level_match: number
      quantification_score: number
      formatting_score: number
      strength_areas: string[]
      weakness_areas: string[]
      total_keywords_found: number
      total_keywords_expected: number
      match_ratio: number
    }
    strengths_analysis: {
      technical_skills: Array<{keyword: string, score: number}>
      quantified_achievements: string[]
      keyword_density_score: number
    }
    weaknesses_analysis: {
      missing_hard_skills: string[]
      missing_soft_skills: string[]
      weak_areas: string[]
      formatting_issues: string[]
    }
  }
}

interface NewAnalysisFormProps {
  onAnalysisComplete: (analysis: Analysis) => void
}

interface AnalysisResultCardProps {
  analysis: Analysis
}

function NewAnalysisForm({ onAnalysisComplete }: NewAnalysisFormProps) {
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setResumeFile(file)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (!resumeFile || !jobDescription.trim()) {
      setError('Please upload a resume and enter a job description')
      return
    }

    setIsAnalyzing(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('resume_file', resumeFile)
      formData.append('job_description', jobDescription)
      if (jobTitle.trim()) {
        formData.append('job_title', jobTitle)
      }

      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8000/analyses/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        onAnalysisComplete(result)
        // Reset form
        setResumeFile(null)
        setJobDescription('')
        setJobTitle('')
        // Reset file input
        const fileInput = document.getElementById('resume-upload') as HTMLInputElement
        if (fileInput) fileInput.value = ''
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Analysis failed. Please try again.')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      setError('Analysis failed. Please check your connection and try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-6">New ATS Analysis</h3>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-red-700 text-sm">{error}</span>
        </div>
      )}

      <div className="space-y-6">
        {/* Resume Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Resume *
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
            <input
              id="resume-upload"
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="resume-upload" className="cursor-pointer">
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">
                {resumeFile ? resumeFile.name : 'Click to upload your resume'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Supports PDF, DOC, DOCX, TXT (Max 10MB)
              </p>
            </label>
          </div>
        </div>

        {/* Job Title (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Title (Optional)
          </label>
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g., Software Engineer, Data Analyst"
            className="input w-full"
          />
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Description *
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the complete job description here..."
            rows={8}
            className="input w-full resize-vertical"
          />
          <p className="text-xs text-gray-500 mt-1">
            {jobDescription.length} characters • Include requirements, skills, and qualifications for best results
          </p>
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !resumeFile || !jobDescription.trim()}
          className="btn btn-primary w-full flex items-center justify-center space-x-2 py-3"
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Target className="h-4 w-4" />
              <span>Analyze Resume</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

function AnalysisResultCard({ analysis }: AnalysisResultCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200'
    if (score >= 60) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  const getMetricColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`
  }

  const details = analysis.analysis_details

  return (
    <div className="space-y-6">
      {/* Main ATS Score Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-gray-900">ATS Analysis Report</h3>
            {analysis.job_title && (
              <p className="text-sm text-gray-600 mt-1 flex items-center">
                <Target className="h-4 w-4 mr-1" />
                {analysis.job_title}
              </p>
            )}
          </div>
          <div className={`px-6 py-4 rounded-xl border-2 ${getScoreBackground(analysis.ats_score)}`}>
            <div className="text-center">
              <div className={`text-3xl font-bold ${getScoreColor(analysis.ats_score)}`}>
                {analysis.ats_score}%
              </div>
              <div className="text-sm font-medium text-gray-600 mt-1">ATS Score</div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        {details?.detailed_analysis && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <Brain className="h-5 w-5 text-blue-600" />
                <span className={`text-sm font-semibold ${getMetricColor(details.detailed_analysis.keyword_density)}`}>
                  {formatPercentage(details.detailed_analysis.keyword_density)}
                </span>
              </div>
              <div className="text-xs text-gray-700 font-medium">Keyword Match</div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span className={`text-sm font-semibold ${getMetricColor(details.detailed_analysis.industry_alignment)}`}>
                  {formatPercentage(details.detailed_analysis.industry_alignment)}
                </span>
              </div>
              <div className="text-xs text-gray-700 font-medium">Industry Fit</div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <Award className="h-5 w-5 text-green-600" />
                <span className={`text-sm font-semibold ${getMetricColor(details.detailed_analysis.experience_level_match)}`}>
                  {formatPercentage(details.detailed_analysis.experience_level_match)}
                </span>
              </div>
              <div className="text-xs text-gray-700 font-medium">Experience Match</div>
            </div>

            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
              <div className="flex items-center justify-between mb-2">
                <Zap className="h-5 w-5 text-orange-600" />
                <span className={`text-sm font-semibold ${getMetricColor(details.detailed_analysis.quantification_score)}`}>
                  {formatPercentage(details.detailed_analysis.quantification_score)}
                </span>
              </div>
              <div className="text-xs text-gray-700 font-medium">Impact Score</div>
            </div>
          </div>
        )}

        {/* Keywords Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strong Keywords */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <h4 className="font-semibold text-gray-900">Strong Keywords</h4>
              <span className="text-sm text-gray-500 bg-green-100 px-2 py-1 rounded-full">
                {analysis.strong_keywords.length}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {analysis.strong_keywords.slice(0, 12).map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-green-100 text-green-800 text-sm rounded-lg font-medium"
                >
                  {keyword}
                </span>
              ))}
              {analysis.strong_keywords.length > 12 && (
                <span className="px-3 py-1.5 bg-gray-100 text-gray-600 text-sm rounded-lg font-medium">
                  +{analysis.strong_keywords.length - 12} more
                </span>
              )}
            </div>
          </div>

          {/* Missing Keywords */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <h4 className="font-semibold text-gray-900">Missing Keywords</h4>
              <span className="text-sm text-gray-500 bg-red-100 px-2 py-1 rounded-full">
                {analysis.missing_keywords.length}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {analysis.missing_keywords.slice(0, 12).map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-red-100 text-red-800 text-sm rounded-lg font-medium"
                >
                  {keyword}
                </span>
              ))}
              {analysis.missing_keywords.length > 12 && (
                <span className="px-3 py-1.5 bg-gray-100 text-gray-600 text-sm rounded-lg font-medium">
                  +{analysis.missing_keywords.length - 12} more
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Analysis Sections */}
      {details && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Strengths Analysis */}
          {details.strengths_analysis && (
            <div className="card">
              <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                Resume Strengths
              </h4>
              
              {/* Technical Skills */}
              {details.strengths_analysis.technical_skills?.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Top Technical Skills</h5>
                  <div className="space-y-2">
                    {details.strengths_analysis.technical_skills.slice(0, 5).map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                        <span className="text-sm font-medium text-gray-900">{skill.keyword}</span>
                        <span className="text-xs text-green-600 font-semibold">
                          {Math.round(skill.score * 100)}% match
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantified Achievements */}
              {details.strengths_analysis.quantified_achievements?.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Quantified Achievements</h5>
                  <div className="space-y-1">
                    {details.strengths_analysis.quantified_achievements.slice(0, 3).map((achievement, index) => (
                      <div key={index} className="text-sm text-gray-600 bg-blue-50 p-2 rounded">
                        ✓ {achievement}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Weaknesses Analysis */}
          {details.weaknesses_analysis && (
            <div className="card">
              <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                Areas for Improvement
              </h4>

              {/* Missing Hard Skills */}
              {details.weaknesses_analysis.missing_hard_skills?.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Missing Technical Skills</h5>
                  <div className="flex flex-wrap gap-1">
                    {details.weaknesses_analysis.missing_hard_skills.slice(0, 6).map((skill, index) => (
                      <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Soft Skills */}
              {details.weaknesses_analysis.missing_soft_skills?.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Missing Soft Skills</h5>
                  <div className="flex flex-wrap gap-1">
                    {details.weaknesses_analysis.missing_soft_skills.slice(0, 4).map((skill, index) => (
                      <span key={index} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Formatting Issues */}
              {details.weaknesses_analysis.formatting_issues?.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Formatting Issues</h5>
                  <div className="space-y-1">
                    {details.weaknesses_analysis.formatting_issues.map((issue, index) => (
                      <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                        • {issue}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Actionable Suggestions */}
      <div className="card">
        <h4 className="font-bold text-gray-900 mb-4 flex items-center">
          <Brain className="h-5 w-5 text-blue-500 mr-2" />
          Actionable Improvement Suggestions
        </h4>
        <div className="space-y-3">
          {analysis.suggestions.map((suggestion, index) => {
            const isCritical = suggestion.includes('CRITICAL') || suggestion.includes('IMMEDIATE')
            const isImportant = suggestion.includes('ACTION:') || suggestion.includes('Add these')
            
            return (
              <div 
                key={index} 
                className={`p-4 rounded-lg border-l-4 ${
                  isCritical 
                    ? 'bg-red-50 border-red-500' 
                    : isImportant 
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                    isCritical 
                      ? 'bg-red-500' 
                      : isImportant 
                      ? 'bg-yellow-500'
                      : 'bg-blue-500'
                  }`}></div>
                  <span className="text-sm text-gray-800 font-medium leading-relaxed">{suggestion}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Analysis Metadata */}
      <div className="text-center py-4 border-t border-gray-200">
        <p className="text-sm text-gray-500">
          Analysis completed on {new Date(analysis.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </p>
        {details?.detailed_analysis && (
          <p className="text-xs text-gray-400 mt-1">
            Keywords Found: {details.detailed_analysis.total_keywords_found} / {details.detailed_analysis.total_keywords_expected} 
            ({formatPercentage(details.detailed_analysis.match_ratio)} match)
          </p>
        )}
      </div>
    </div>
  )
}

export default function StudentDashboard() {
  const { user, logout, loading } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview')
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loadingAnalyses, setLoadingAnalyses] = useState(false)

  useEffect(() => {
    if (!loading && (!user || user.role !== 'student')) {
      router.push('/auth/login')
      return
    }

    if (user) {
      fetchAnalyses()
    }
  }, [user, loading, router])

  const fetchAnalyses = async () => {
    setLoadingAnalyses(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8000/analyses/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setAnalyses(data)
      }
    } catch (error) {
      console.error('Error fetching analyses:', error)
    } finally {
      setLoadingAnalyses(false)
    }
  }

  const handleAnalysisComplete = (newAnalysis: Analysis) => {
    setAnalyses([newAnalysis, ...analyses])
    setActiveTab('results')
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-2">
              <Target className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">GetPlaced</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.full_name}</span>
              <button
                onClick={logout}
                className="btn btn-outline px-4 py-2"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'analyze', label: 'New Analysis', icon: Plus },
              { id: 'results', label: 'Results', icon: Eye },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Welcome Message */}
            <div className="card">
              <div className="text-center py-8">
                <Target className="h-16 w-16 text-primary-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to ResumeATS</h2>
                <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                  Get real ATS scores for your resume, identify missing keywords, and receive
                  personalized suggestions to improve your job application success rate.
                </p>
                <button
                  onClick={() => setActiveTab('analyze')}
                  className="btn btn-primary flex items-center space-x-2 mx-auto"
                >
                  <Plus className="h-4 w-4" />
                  <span>Start New Analysis</span>
                </button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="card">
                <div className="flex items-center">
                  <Target className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Analyses</p>
                    <p className="text-2xl font-bold text-gray-900">{analyses.length}</p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <BarChart3 className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Avg. ATS Score</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analyses.length > 0 
                        ? Math.round(analyses.reduce((acc, r) => acc + r.ats_score, 0) / analyses.length)
                        : 0}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Best Score</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analyses.length > 0 
                        ? Math.max(...analyses.map(a => a.ats_score))
                        : 0}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Analyses */}
            {analyses.length > 0 && (
              <div className="card">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Recent Analyses</h3>
                  <button
                    onClick={() => setActiveTab('results')}
                    className="text-primary-600 hover:text-primary-500 text-sm"
                  >
                    View all
                  </button>
                </div>
                
                <div className="space-y-3">
                  {analyses.slice(0, 3).map((analysis) => (
                    <div key={analysis.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Target className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">
                            {analysis.job_title || 'Job Analysis'}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(analysis.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`text-lg font-bold ${getScoreColor(analysis.ats_score)}`}>
                          {analysis.ats_score}%
                        </p>
                        <p className="text-xs text-gray-500">ATS Score</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* New Analysis Tab */}
        {activeTab === 'analyze' && (
          <NewAnalysisForm onAnalysisComplete={handleAnalysisComplete} />
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <button
                onClick={() => setActiveTab('analyze')}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>New Analysis</span>
              </button>
            </div>

            {loadingAnalyses ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading analyses...</p>
              </div>
            ) : analyses.length === 0 ? (
              <div className="card text-center py-12">
                <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
                <p className="text-gray-600 mb-6">Start by analyzing your resume against a job description</p>
                <button
                  onClick={() => setActiveTab('analyze')}
                  className="btn btn-primary"
                >
                  Start Analysis
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {analyses.map((analysis) => (
                  <AnalysisResultCard key={analysis.id} analysis={analysis} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}