import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable detailed fetch logging in development
  logging: {
    fetches: {
      fullUrl: true,
    },
  },

  // Increase the API route body limit to 50 MB for large document uploads
  experimental: {
    serverActions: {
      bodySizeLimit: "52mb",
    },
  },

  // Vercel: allow up to 60s for the /api/convert and /api/generate-excel routes
  // (large document parsing can be slow)
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
        ],
      },
    ];
  },
};

export default nextConfig;
