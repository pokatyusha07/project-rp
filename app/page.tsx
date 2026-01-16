/**
 * Главная страница приложения
 */
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function HomePage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Проверяем наличие токена
    const token = localStorage.getItem("access_token")
    setIsAuthenticated(!!token)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      <div className="container mx-auto px-4 py-16">
        {/* Hero секция */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 text-balance">Система обработки звонков</h1>
          <p className="text-xl text-muted-foreground mb-8 text-balance max-w-2xl mx-auto">
            Автоматическая транскрипция речи, интеллектуальный анализ и визуализация данных
          </p>

          {isAuthenticated ? (
            <div className="flex gap-4 justify-center">
              <Button size="lg" onClick={() => router.push("/dashboard")}>
                Открыть панель управления
              </Button>
              <Button size="lg" variant="outline" onClick={() => router.push("/calls/upload")}>
                Загрузить звонок
              </Button>
            </div>
          ) : (
            <div className="flex gap-4 justify-center">
              <Button size="lg" onClick={() => router.push("/auth/login")}>
                Войти
              </Button>
              <Button size="lg" variant="outline" onClick={() => router.push("/auth/register")}>
                Регистрация
              </Button>
            </div>
          )}
        </div>

        {/* Особенности */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🎤</span>
                Транскрипция
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Автоматическое распознавание речи с использованием Whisper AI. Поддержка русского и английского языков.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📊</span>
                Анализ
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Интеллектуальный анализ содержания: выделение ключевых слов, определение категории и тональности
                разговора.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📈</span>
                Аналитика
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Визуализация статистики, поиск по транскрипциям, экспорт отчетов и интеграция с Telegram.
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Возможности */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Возможности системы</h2>

          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Real-time транскрипция</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Отслеживайте процесс транскрипции в реальном времени через WebSocket. Промежуточные результаты
                  отображаются сразу по мере обработки.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Telegram интеграция</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Отправляйте голосовые сообщения прямо в Telegram бот. Получайте уведомления о готовности транскрипции
                  и просматривайте аналитику.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Поиск и фильтрация</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Мощный поиск по текстам транскрипций и ключевым словам. Фильтрация по категориям, датам и статусам.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
