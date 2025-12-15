/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ["@repo/ui"],
    images: {
        domains: [
            "files.tampabaycreditrepair.com",
            "lh3.googleusercontent.com",
            "avatars.githubusercontent.com"
        ],
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '**',
            },
        ],
    },
    // Optional: Use experimental edge runtime if fully compatible, 
    // but standard node runtime is better supported for complex apps on Pages now via Node compat.
}

// Injected by @cloudflare/next-on-pages
if (process.env.NODE_ENV === 'development') {
    const { setupDevPlatform } = require('@cloudflare/next-on-pages/next-dev');
    setupDevPlatform();
}

module.exports = nextConfig
