import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Nav } from "@/components/nav"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Sentinella — AI Governance Console",
  description: "Sovereign AI governance control plane operator interface",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50`}>
        <div className="flex min-h-screen">
          <Nav />
          <main className="flex-1 p-8 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
