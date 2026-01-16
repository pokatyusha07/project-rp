/**
 * Главная панель управления с аналитикой
 */
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { api, type Statistics } from "@/lib/api"
import { DashboardLayout } from "@/components/dashboard-layout"
import { StatsCards } from "@/components/stats-cards"
import { CallsChart } from "@/components/calls-chart"
import { CategoriesChart } from "@/components/categories-chart"
import { useToast } from "@/hooks/use-toast"

export default function DashboardPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<Statistics | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const data = await api.getStatistics()
      setStats(data)
    } catch (error) {
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить статистику",
        variant: "destructive",
      })

      // Если ошибка авторизации, перенаправляем на вход
      router.push("/auth/login")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Загрузка данных...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Панель управления</h1>
            <p className="text-muted-foreground">Обзор статистики и аналитики звонков</p>
          </div>
          <Button onClick={() => router.push("/calls/upload")}>Загрузить звонок</Button>
        </div>

        {stats && <StatsCards stats={stats} />}

        <div className="grid md:grid-cols-2 gap-6">
          <CallsChart />
          <CategoriesChart />
        </div>
      </div>
    </DashboardLayout>
  )
}
