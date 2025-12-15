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
    },
}

module.exports = nextConfig
