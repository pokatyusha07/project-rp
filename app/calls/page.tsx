/**
 * Страница списка звонков
 */
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { api, type Call } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function CallsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [calls, setCalls] = useState<Call[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    loadCalls()
  }, [])

  const loadCalls = async () => {
    try {
      const data = await api.getCalls()
      setCalls(data.results)
    } catch (error) {
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить список звонков",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadCalls()
      return
    }

    setSearching(true)
    try {
      const results = await api.searchCalls(searchQuery)
      setCalls(results)
    } catch (error) {
      toast({
        title: "Ошибка поиска",
        description: "Не удалось выполнить поиск",
        variant: "destructive",
      })
    } finally {
      setSearching(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      pending: "secondary",
      processing: "default",
      completed: "outline",
      failed: "destructive",
    }

    return <Badge variant={variants[status] || "default"}>{status}</Badge>
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Загрузка звонков...</p>
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
            <h1 className="text-3xl font-bold">Мои звонки</h1>
            <p className="text-muted-foreground">Список всех загруженных звонков</p>
          </div>
          <Button onClick={() => router.push("/calls/upload")}>Загрузить звонок</Button>
        </div>

        {/* Поиск */}
        <div className="flex gap-2">
          <Input
            placeholder="Поиск по транскрипциям..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={searching}>
            {searching ? "Поиск..." : "Найти"}
          </Button>
          {searchQuery && (
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery("")
                loadCalls()
              }}
            >
              Сбросить
            </Button>
          )}
        </div>

        {/* Список звонков */}
        {calls.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground mb-4">Звонков не найдено</p>
              <Button onClick={() => router.push("/calls/upload")}>Загрузить первый звонок</Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {calls.map((call) => (
              <Card
                key={call.id}
                className="cursor-pointer hover:border-primary transition-colors"
                onClick={() => router.push(`/calls/${call.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">ID: {call.id.substring(0, 8)}...</CardTitle>
                      <CardDescription>{new Date(call.created_at).toLocaleString("ru-RU")}</CardDescription>
                    </div>
                    {getStatusBadge(call.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Длительность</p>
                      <p className="font-medium">{call.duration?.toFixed(1) || 0}с</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Язык</p>
                      <p className="font-medium">{call.language.toUpperCase()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Транскрипция</p>
                      <p className="font-medium">{call.has_transcription ? "✅ Готова" : "⏳ В процессе"}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Анализ</p>
                      <p className="font-medium">{call.has_analysis ? "✅ Готов" : "⏳ В процессе"}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
