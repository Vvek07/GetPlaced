/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const apiUrl = process.env.NODE_ENV === 'production' 
      ? process.env.NEXT_PUBLIC_API_URL || 'https://getplaced-backend.railway.app'
      : 'http://127.0.0.1:8000'
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
      // Handle legacy v1 API routes for backwards compatibility
      {
        source: '/api/v1/analysis/:path*',
        destination: `${apiUrl}/analyses/:path*`,
      },
    ]
  },
  // Enable hot reloading
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  },
}

module.exports = nextConfig