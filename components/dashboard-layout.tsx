/**
 * Общий layout для страниц панели управления
 */
"use client"

import type React from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = () => {
    api.logout()
    router.push("/")
  }

  const navItems = [
    { href: "/dashboard", label: "Панель управления", icon: "📊" },
    { href: "/calls", label: "Звонки", icon: "📞" },
    { href: "/calls/upload", label: "Загрузить", icon: "⬆️" },
    { href: "/analytics", label: "Аналитика", icon: "📈" },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="text-xl font-bold">
              Call System
            </Link>

            <nav className="hidden md:flex gap-6">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 hover:text-primary transition-colors ${
                    pathname === item.href ? "text-primary font-medium" : "text-muted-foreground"
                  }`}
                >
                  <span>{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>

            <Button variant="outline" onClick={handleLogout}>
              Выйти
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
