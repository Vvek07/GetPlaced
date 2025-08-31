'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { Eye, EyeOff, Mail, Lock, User, Phone, Building, GraduationCap, Calendar } from 'lucide-react'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    role: 'student',
    phone: '',
    university: '',
    department: '',
    graduation_year: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    setLoading(true)

    try {
      const registrationData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role,
        phone: formData.phone || undefined,
        university: formData.university || undefined,
        department: formData.department || undefined,
        graduation_year: formData.graduation_year ? parseInt(formData.graduation_year) : undefined
      }

      await register(registrationData)
      
      // Redirect based on role
      switch (formData.role) {
        case 'student':
          router.push('/dashboard/student')
          break
        case 'recruiter':
          router.push('/dashboard/recruiter')
          break
        case 'faculty':
          router.push('/dashboard/faculty')
          break
        default:
          router.push('/dashboard')
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join GetPlaced - your smart ATS platform
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Full Name */}
            <div>
              <label htmlFor="full_name" className="label">
                Full Name *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  required
                  className="input pl-10"
                  placeholder="Enter your full name"
                  value={formData.full_name}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="label">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="input pl-10"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Role */}
            <div>
              <label htmlFor="role" className="label">
                Role *
              </label>
              <select
                id="role"
                name="role"
                required
                className="input"
                value={formData.role}
                onChange={handleChange}
              >
                <option value="student">Student</option>
                <option value="recruiter">Recruiter</option>
                <option value="faculty">Faculty</option>
              </select>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="label">
                Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  className="input pl-10 pr-10"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 h-4 w-4 text-gray-400"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="label">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  className="input pl-10 pr-10"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 h-4 w-4 text-gray-400"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="label">
                Phone Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  className="input pl-10"
                  placeholder="Enter your phone number"
                  value={formData.phone}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* University */}
            <div>
              <label htmlFor="university" className="label">
                University/Institution
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="university"
                  name="university"
                  type="text"
                  className="input pl-10"
                  placeholder="Enter your university name"
                  value={formData.university}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Department */}
            <div>
              <label htmlFor="department" className="label">
                Department/Field
              </label>
              <div className="relative">
                <GraduationCap className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  id="department"
                  name="department"
                  type="text"
                  className="input pl-10"
                  placeholder="e.g., Computer Science"
                  value={formData.department}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Graduation Year */}
            {formData.role === 'student' && (
              <div>
                <label htmlFor="graduation_year" className="label">
                  Expected Graduation Year
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <input
                    id="graduation_year"
                    name="graduation_year"
                    type="number"
                    min="2020"
                    max="2030"
                    className="input pl-10"
                    placeholder="e.g., 2024"
                    value={formData.graduation_year}
                    onChange={handleChange}
                  />
                </div>
              </div>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-3 text-lg disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-primary-600 hover:text-primary-500">
                Sign in here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}