"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/events", label: "Audit Log" },
  { href: "/models", label: "Model Registry" },
]

export function Nav() {
  const pathname = usePathname()

  return (
    <nav className="w-56 min-h-screen bg-slate-900 text-slate-300 flex flex-col px-4 py-6 gap-1">
      <div className="mb-6 px-2">
        <span className="text-white font-semibold tracking-tight text-sm">Sentinella</span>
        <p className="text-slate-500 text-xs mt-0.5">AI Governance</p>
      </div>
      {links.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={`px-3 py-2 rounded text-sm transition-colors ${
            pathname === href
              ? "bg-slate-700 text-white"
              : "hover:bg-slate-800 hover:text-white"
          }`}
        >
          {label}
        </Link>
      ))}
    </nav>
  )
}
