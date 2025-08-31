import Link from 'next/link'
import { ArrowRight, Upload, BarChart3, FileText, Target, Brain, TrendingUp, CheckCircle, Shield, Star, Zap, Linkedin, Github, Twitter, Mail, Phone, Heart } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <Target className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">GetPlaced</h1>
                <p className="text-xs text-gray-500">Smart ATS Analyzer</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Link href="/auth/login" className="btn btn-ghost">Sign In</Link>
              <Link href="/auth/register" className="btn btn-primary">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="section bg-gradient-primary">
        <div className="container text-center">
          <div className="max-w-4xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
              <Zap className="w-4 h-4 mr-2" />
              AI-Powered ATS Analysis
            </div>
            <h1 className="heading-xl text-gray-900 mb-6 text-balance">
              Get <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Placed</span> with Confidence
            </h1>
            <p className="text-xl text-muted leading-relaxed mb-10 max-w-2xl mx-auto">
              Upload your resume and job description to get an instant ATS compatibility score, missing keywords analysis, and personalized improvement suggestions.
            </p>
            <Link href="/auth/register" className="btn btn-primary btn-lg">
              <Upload className="w-5 h-5 mr-2" /> Start Analysis
            </Link>
            
            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-muted mt-8">
              <div className="flex items-center">
                <Shield className="w-4 h-4 mr-2 text-green-500" />
                Secure & Private
              </div>
              <div className="flex items-center">
                <Star className="w-4 h-4 mr-2 text-yellow-500" />
                Real ATS Scoring
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 text-blue-500" />
                Instant Results
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 mb-4">Everything You Need for ATS Success</h2>
            <p className="text-xl text-muted max-w-2xl mx-auto">
              Powerful ATS analysis tools designed to improve your resume and job application success
            </p>
          </div>
          <div className="grid lg:grid-cols-3 md:grid-cols-2 gap-8">
            <div className="card card-hover group">
              <div className="icon-container-lg group-hover:scale-110 transition-transform duration-300">
                <BarChart3 className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Real ATS Score</h3>
              <p className="text-muted mb-4">Get your actual ATS compatibility score based on how recruiting systems evaluate your resume against job descriptions.</p>
              <div className="flex items-center text-blue-600 font-medium text-sm">
                Learn more <ArrowRight className="ml-1 w-4 h-4" />
              </div>
            </div>
            <div className="card card-hover group">
              <div className="icon-container-lg group-hover:scale-110 transition-transform duration-300">
                <Target className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Missing Keywords</h3>
              <p className="text-muted mb-4">Identify exactly which keywords from the job description are missing from your resume and need to be added.</p>
              <div className="flex items-center text-blue-600 font-medium text-sm">
                Learn more <ArrowRight className="ml-1 w-4 h-4" />
              </div>
            </div>
            <div className="card card-hover group">
              <div className="icon-container-lg group-hover:scale-110 transition-transform duration-300">
                <Brain className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Smart Suggestions</h3>
              <p className="text-muted mb-4">Get AI-powered recommendations on exactly what to add to your resume to improve your ATS score.</p>
              <div className="flex items-center text-blue-600 font-medium text-sm">
                Learn more <ArrowRight className="ml-1 w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section bg-gray-50">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="heading-lg text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-muted max-w-2xl mx-auto">
              Get your ATS score in three simple steps
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                1
              </div>
              <h3 className="text-lg font-semibold mb-2">Upload Resume</h3>
              <p className="text-muted">Upload your resume in PDF, DOC, or TXT format</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                2
              </div>
              <h3 className="text-lg font-semibold mb-2">Paste Job Description</h3>
              <p className="text-muted">Copy and paste the job description you're applying for</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                3
              </div>
              <h3 className="text-lg font-semibold mb-2">Get Results</h3>
              <p className="text-muted">Receive your ATS score, missing keywords, and improvement suggestions</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="container text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="heading-lg text-gray-900 mb-4">
              Ready to Improve Your Resume?
            </h2>
            <p className="text-xl text-muted mb-8">
              Start analyzing your resume today and increase your chances of getting hired
            </p>
            <Link href="/auth/register" className="btn btn-primary btn-lg">
              Get Started for Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="container py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {/* Brand Section */}
            <div className="md:col-span-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                  <Target className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">GetPlaced</h3>
                  <p className="text-sm text-gray-400">Smart ATS Analyzer</p>
                </div>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed max-w-sm">
                AI-powered resume analysis platform designed to help you get placed in your dream job with confidence and precision.
              </p>
            </div>

            {/* Contact Info */}
            <div className="md:col-span-1">
              <h4 className="font-semibold text-white mb-4 flex items-center">
                <Mail className="h-4 w-4 mr-2 text-blue-400" />
                Get in Touch
              </h4>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Mail className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <a href="mailto:vivekpatil9944@gmail.com" className="text-gray-300 hover:text-blue-400 transition-colors text-sm">
                    vivekpatil9944@gmail.com
                  </a>
                </div>
                <div className="flex items-center space-x-3">
                  <Phone className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <a href="tel:+919922359944" className="text-gray-300 hover:text-blue-400 transition-colors text-sm">
                    +91 99223 59944
                  </a>
                </div>
              </div>
            </div>

            {/* Social Links */}
            <div className="md:col-span-1">
              <h4 className="font-semibold text-white mb-4">Connect With Me</h4>
              <div className="flex space-x-4">
                <a 
                  href="https://www.linkedin.com/in/vvek07" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 hover:bg-blue-600 rounded-lg flex items-center justify-center transition-colors group"
                >
                  <Linkedin className="h-5 w-5 text-gray-400 group-hover:text-white" />
                </a>
                <a 
                  href="https://www.github.com/Vvek07" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-center transition-colors group"
                >
                  <Github className="h-5 w-5 text-gray-400 group-hover:text-white" />
                </a>
                <a 
                  href="https://mobile.x.com/vivekpatil011" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 hover:bg-blue-500 rounded-lg flex items-center justify-center transition-colors group"
                >
                  <Twitter className="h-5 w-5 text-gray-400 group-hover:text-white" />
                </a>
              </div>
              <p className="text-xs text-gray-400 mt-4">
                For more information or collaboration opportunities, feel free to reach out!
              </p>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-800 pt-6">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-2 md:space-y-0">
              <div className="flex items-center space-x-1 text-sm text-gray-400">
                <span>Made with</span>
                <Heart className="h-4 w-4 text-red-500 animate-pulse" />
                <span>by</span>
                <span className="font-semibold text-blue-400">Vivek Patil</span>
                <span className="text-gray-500">• © 2025 GetPlaced</span>
              </div>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>Built with Next.js & FastAPI</span>
                <span className="w-1 h-1 bg-gray-600 rounded-full"></span>
                <span>Powered by AI</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
