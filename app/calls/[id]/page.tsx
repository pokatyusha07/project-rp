/**
 * Страница детального просмотра звонка с real-time обновлениями
 */
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { api, type CallDetail } from "@/lib/api"
import { wsClient } from "@/lib/websocket"
import { useToast } from "@/hooks/use-toast"

export default function CallDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const callId = params.id as string

  const [call, setCall] = useState<CallDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [currentSegment, setCurrentSegment] = useState("")

  useEffect(() => {
    loadCall()
    setupWebSocket()

    return () => {
      wsClient.disconnect()
    }
  }, [callId])

  const loadCall = async () => {
    try {
      const data = await api.getCallDetail(callId)
      setCall(data)
    } catch (error) {
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить информацию о звонке",
        variant: "destructive",
      })
      router.push("/calls")
    } finally {
      setLoading(false)
    }
  }

  const setupWebSocket = () => {
    const token = localStorage.getItem("access_token")
    if (!token) return

    wsClient.connectToCall(callId, token)

    // Подписываемся на события
    wsClient.on("transcription_progress", (data) => {
      setProgress(data.progress)
      setCurrentSegment(data.text)
    })

    wsClient.on("transcription_completed", (data) => {
      setProgress(100)
      loadCall() // Перезагружаем данные
      toast({
        title: "Транскрипция готова",
        description: "Текст успешно распознан",
      })
    })

    wsClient.on("status_update", (data) => {
      loadCall() // Обновляем данные при изменении статуса
    })

    wsClient.on("transcription_error", (data) => {
      toast({
        title: "Ошибка транскрипции",
        description: data.error,
        variant: "destructive",
      })
    })
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Загрузка звонка...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!call) {
    return null
  }

  const isProcessing = call.status === "processing"

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Заголовок */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Звонок {call.id.substring(0, 8)}</h1>
            <p className="text-muted-foreground">{new Date(call.created_at).toLocaleString("ru-RU")}</p>
          </div>
          <Button variant="outline" onClick={() => router.push("/calls")}>
            Назад к списку
          </Button>
        </div>

        {/* Прогресс обработки */}
        {isProcessing && (
          <Card>
            <CardHeader>
              <CardTitle>Обработка звонка</CardTitle>
              <CardDescription>Транскрипция в процессе...</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Progress value={progress} />
              <p className="text-sm text-muted-foreground">Прогресс: {progress}%</p>
              {currentSegment && (
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm font-medium mb-1">Текущий сегмент:</p>
                  <p className="text-sm">{currentSegment}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Основная информация */}
        <Card>
          <CardHeader>
            <CardTitle>Информация</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Статус</p>
                <Badge className="mt-1">{call.status_display}</Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Длительность</p>
                <p className="font-medium mt-1">{call.duration?.toFixed(1) || 0} секунд</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Язык</p>
                <p className="font-medium mt-1">{call.language.toUpperCase()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Результаты */}
        {call.transcription && (
          <Tabs defaultValue="transcription" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="transcription">Транскрипция</TabsTrigger>
              <TabsTrigger value="analysis">Анализ</TabsTrigger>
            </TabsList>

            <TabsContent value="transcription">
              <Card>
                <CardHeader>
                  <CardTitle>Текст транскрипции</CardTitle>
                  <CardDescription>Уверенность: {call.transcription.confidence?.toFixed(1)}%</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    <p className="whitespace-pre-wrap">{call.transcription.text}</p>
                  </div>

                  {/* Сегменты */}
                  {call.transcription.segments && call.transcription.segments.length > 0 && (
                    <div className="mt-6 space-y-2">
                      <h3 className="font-semibold">Сегменты по времени</h3>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {call.transcription.segments.map((segment, index) => (
                          <div key={index} className="p-3 bg-muted rounded-lg text-sm">
                            <p className="text-muted-foreground mb-1">
                              {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                            </p>
                            <p>{segment.text}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analysis">
              {call.analysis ? (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Общий анализ</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Категория</p>
                          <p className="font-medium mt-1">{call.analysis.category_display || "Не определена"}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Тональность</p>
                          <p className="font-medium mt-1">
                            {call.analysis.sentiment === "positive" && "😊 Позитивная"}
                            {call.analysis.sentiment === "neutral" && "😐 Нейтральная"}
                            {call.analysis.sentiment === "negative" && "😞 Негативная"}
                          </p>
                        </div>
                      </div>

                      {call.analysis.summary && (
                        <div>
                          <p className="text-sm text-muted-foreground mb-2">Краткое содержание</p>
                          <p className="whitespace-pre-wrap">{call.analysis.summary}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Ключевые слова</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {call.analysis.keywords.map((keyword, index) => (
                          <Badge key={index} variant="secondary">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {call.analysis.word_frequency && Object.keys(call.analysis.word_frequency).length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Частота слов</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 max-h-64 overflow-y-auto">
                          {Object.entries(call.analysis.word_frequency)
                            .slice(0, 20)
                            .map(([word, count]) => (
                              <div key={word} className="flex items-center justify-between text-sm">
                                <span>{word}</span>
                                <Badge variant="outline">{count}</Badge>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <Card>
                  <CardContent className="py-12 text-center">
                    <p className="text-muted-foreground">Анализ еще не готов</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        )}
      </div>
    </DashboardLayout>
  )
}
