import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs'
import { Shield, TrendingUp, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-400" />
              <span className="text-xl font-bold text-white">PhishGuard</span>
            </div>
            <div className="flex items-center gap-4">
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                    Sign In
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <Link
                  href="/dashboard"
                  className="px-4 py-2 text-white hover:text-blue-400 transition-colors"
                >
                  Dashboard
                </Link>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm font-medium mb-8">
            <Shield className="w-4 h-4" />
            AI-Powered Phishing Detection
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Protect Yourself from
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Phishing Attacks
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Real-time phishing detection powered by Machine Learning, Threat Intelligence, 
            and Visual Similarity Analysis. Stay safe online with PhishGuard.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-lg transition-all hover:scale-105 flex items-center justify-center gap-2">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/dashboard"
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-lg transition-all hover:scale-105 flex items-center justify-center gap-2"
              >
                Go to Dashboard
                <ArrowRight className="w-5 h-5" />
              </Link>
            </SignedIn>
            <a
              href="https://github.com/yourusername/phishguard"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold text-lg transition-all border border-white/20"
            >
              View on GitHub
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-24">
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Machine Learning</h3>
            <p className="text-gray-400">
              Advanced ML models analyze 47+ URL features with LightGBM and DistilBERT for accurate detection.
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
              <AlertTriangle className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Threat Intelligence</h3>
            <p className="text-gray-400">
              Real-time integration with VirusTotal, URLhaus, and AbuseIPDB for comprehensive threat data.
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all">
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
              <CheckCircle className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Visual Similarity</h3>
            <p className="text-gray-400">
              Detect brand impersonation using perceptual hashing and vector similarity search.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-8 mt-24">
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">95%+</div>
            <div className="text-gray-400">Detection Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">&lt;2s</div>
            <div className="text-gray-400">Average Scan Time</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">47</div>
            <div className="text-gray-400">URL Features</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">24/7</div>
            <div className="text-gray-400">Real-time Protection</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-black/20 backdrop-blur-lg mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <Shield className="w-6 h-6 text-blue-400" />
              <span className="text-white font-semibold">PhishGuard</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2024 PhishGuard. Built with ❤️ for a safer internet.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
