import type { Metadata, Viewport } from 'next'
import { Inter, Poppins } from 'next/font/google'
import { Toaster } from '@/components/ui/sonner'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { AuthProvider } from '@/components/providers/auth-provider'
import './globals.css'

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
    display: 'swap'
})

const poppins = Poppins({
    weight: ['400', '500', '600', '700', '800', '900'],
    subsets: ['latin'],
    variable: '--font-poppins',
    display: 'swap'
})

export const metadata: Metadata = {
    metadataBase: new URL('https://tampabycreditrepair.com'),
    title: {
        default: 'Tampa Bay Credit Repair | Fix Your Credit Score Fast',
        template: '%s | Tampa Bay Credit Repair'
    },
    description: 'Professional credit repair services in Tampa Bay. Remove negative items, boost your credit score, and achieve financial freedom. Free consultation available.',
    keywords: [
        'credit repair Tampa Bay',
        'credit repair Tampa',
        'fix credit score Florida',
        'remove negative items',
        'credit restoration',
        'debt collection removal',
        'Tampa credit specialist'
    ],
    authors: [{ name: 'RJ Business Solutions', url: 'https://rickjeffersonsolutions.com' }],
    creator: 'Rick Jefferson',
    publisher: 'RJ Business Solutions',
    openGraph: {
        type: 'website',
        locale: 'en_US',
        url: 'https://tampabaycreditrepair.com',
        siteName: 'Tampa Bay Credit Repair',
        title: 'Tampa Bay Credit Repair | Fix Your Credit Score Fast',
        description: 'Professional credit repair services in Tampa Bay. Remove negative items and boost your credit score.',
        images: [
            {
                url: '/og-image.png',
                width: 1200,
                height: 630,
                alt: 'Tampa Bay Credit Repair'
            }
        ]
    },
    twitter: {
        card: 'summary_large_image',
        title: 'Tampa Bay Credit Repair | Fix Your Credit Score Fast',
        description: 'Professional credit repair services in Tampa Bay.',
        images: ['/og-image.png'],
        creator: '@ricksolutions1'
    },
}

export const viewport: Viewport = {
    themeColor: [
        { media: '(prefers-color-scheme: light)', color: '#ffffff' },
        { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' }
    ],
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5
}

export default function RootLayout({
    children
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${inter.variable} ${poppins.variable} font-sans antialiased`}>
                <ThemeProvider
                    attribute="class"
                    defaultTheme="dark"
                    enableSystem
                    disableTransitionOnChange
                >
                    <AuthProvider>
                        {children}
                        <Toaster />
                    </AuthProvider>
                </ThemeProvider>
            </body>
        </html>
    )
}
