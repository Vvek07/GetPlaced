/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/:path*',
      },
      // Handle legacy v1 API routes for backwards compatibility
      {
        source: '/api/v1/analysis/:path*',
        destination: 'http://127.0.0.1:8000/analyses/:path*',
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