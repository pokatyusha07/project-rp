/**
 * Страница расширенной аналитики
 */
"use client"

import { useEffect, useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function AnalyticsPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [keywords, setKeywords] = useState<Array<{ keyword: string; count: number }>>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const keywordsData = await api.getTopKeywords(30)
      setKeywords(keywordsData)
    } catch (error) {
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить аналитику",
        variant: "destructive",
      })
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
            <p className="text-muted-foreground">Загрузка аналитики...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Расширенная аналитика</h1>
          <p className="text-muted-foreground">Детальный анализ всех звонков</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Топ ключевых слов</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {keywords.map((item, index) => (
                  <div key={item.keyword} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-6">{index + 1}.</span>
                      <span className="font-medium">{item.keyword}</span>
                    </div>
                    <Badge variant="secondary">{item.count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Информация</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Здесь отображаются наиболее часто встречающиеся слова во всех ваших транскрипциях.
              </p>
              <p className="text-sm text-muted-foreground">
                Используйте эту информацию для анализа основных тем обсуждений и выявления трендов.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
