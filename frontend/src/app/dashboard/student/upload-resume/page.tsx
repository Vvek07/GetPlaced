'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function UploadResumePage() {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [error, setError] = useState('')

  const { user, token } = useAuth()
  const router = useRouter()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedFile(file)
      setError('')
      setUploadResult(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    onError: (error) => {
      setError(error.message)
    }
  })

  const uploadResume = async () => {
    if (!uploadedFile || !token) return

    setUploading(true)
    setError('')
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', uploadedFile)

      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100
          setUploadProgress(percentComplete)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText)
          setUploadResult(result)
          setUploadProgress(100)
        } else {
          const error = JSON.parse(xhr.responseText)
          setError(error.detail || 'Upload failed')
        }
        setUploading(false)
      })

      xhr.addEventListener('error', () => {
        setError('Upload failed due to network error')
        setUploading(false)
      })

      xhr.open('POST', '/api/resumes/upload')
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(formData)

    } catch (err: any) {
      setError(err.message || 'Upload failed')
      setUploading(false)
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    setUploadResult(null)
    setError('')
    setUploadProgress(0)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard/student"
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Upload Resume</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Instructions */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Upload Instructions</h2>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• Upload your resume in PDF, DOC, DOCX, or TXT format</p>
              <p>• Maximum file size: 10MB</p>
              <p>• Our AI will automatically extract skills, experience, and education</p>
              <p>• You'll receive a quality score and improvement suggestions</p>
              <p>• We'll find matching job opportunities based on your profile</p>
            </div>
          </div>

          {/* Upload Area */}
          <div className="card">
            {!uploadedFile && !uploadResult && (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
                </p>
                <p className="text-gray-600 mb-4">
                  Drag and drop your file here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF, DOC, DOCX, TXT (max 10MB)
                </p>
              </div>
            )}

            {uploadedFile && !uploadResult && (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <File className="h-8 w-8 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(uploadedFile.size)}</p>
                    </div>
                  </div>
                  <button
                    onClick={removeFile}
                    className="text-gray-400 hover:text-red-500"
                    disabled={uploading}
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {error && (
                  <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                    <p className="text-red-700">{error}</p>
                  </div>
                )}

                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading and processing...</span>
                      <span>{Math.round(uploadProgress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="flex space-x-4">
                  <button
                    onClick={uploadResume}
                    disabled={uploading}
                    className="btn btn-primary flex-1 disabled:opacity-50"
                  >
                    {uploading ? 'Processing...' : 'Upload & Analyze'}
                  </button>
                  <button
                    onClick={removeFile}
                    disabled={uploading}
                    className="btn btn-outline"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {uploadResult && (
              <div className="space-y-6">
                <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-500" />
                  <div>
                    <p className="font-medium text-green-900">Resume uploaded successfully!</p>
                    <p className="text-sm text-green-700">
                      Your resume has been processed and analyzed.
                    </p>
                  </div>
                </div>

                {/* Resume Analysis Preview */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Processing Status</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">File Upload</span>
                        <span className="text-sm text-green-600">✓ Complete</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Text Extraction</span>
                        <span className="text-sm text-green-600">✓ Complete</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Skill Analysis</span>
                        <span className="text-sm text-green-600">✓ Complete</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Quality Assessment</span>
                        <span className="text-sm text-green-600">✓ Complete</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Quick Stats</h3>
                    <div className="space-y-2">
                      {uploadResult.quality_score && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Quality Score</span>
                          <span className="text-sm font-medium text-gray-900">
                            {Math.round(uploadResult.quality_score)}%
                          </span>
                        </div>
                      )}
                      {uploadResult.skills && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Skills Found</span>
                          <span className="text-sm font-medium text-gray-900">
                            {uploadResult.skills.length}
                          </span>
                        </div>
                      )}
                      {uploadResult.experience && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Experience Entries</span>
                          <span className="text-sm font-medium text-gray-900">
                            {uploadResult.experience.length}
                          </span>
                        </div>
                      )}
                      {uploadResult.education && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Education Entries</span>
                          <span className="text-sm font-medium text-gray-900">
                            {uploadResult.education.length}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Skills Preview */}
                {uploadResult.skills && uploadResult.skills.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Extracted Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {uploadResult.skills.slice(0, 15).map((skill: string, index: number) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                      {uploadResult.skills.length > 15 && (
                        <span className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
                          +{uploadResult.skills.length - 15} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-4">
                  <Link
                    href={`/dashboard/student/resume/${uploadResult.id}/analysis`}
                    className="btn btn-primary"
                  >
                    View Detailed Analysis
                  </Link>
                  <Link
                    href="/dashboard/student"
                    className="btn btn-outline"
                  >
                    Back to Dashboard
                  </Link>
                  <button
                    onClick={() => {
                      setUploadedFile(null)
                      setUploadResult(null)
                      setError('')
                    }}
                    className="btn btn-secondary"
                  >
                    Upload Another
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="card">
            <h3 className="font-medium text-gray-900 mb-3">Tips for Better Results</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div className="space-y-2">
                <p>• Use a clear, standard resume format</p>
                <p>• Include specific technical skills</p>
                <p>• List relevant work experience with details</p>
                <p>• Include education and certifications</p>
              </div>
              <div className="space-y-2">
                <p>• Use industry-standard terminology</p>
                <p>• Include quantifiable achievements</p>
                <p>• Ensure contact information is visible</p>
                <p>• Save as PDF for best text extraction</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}