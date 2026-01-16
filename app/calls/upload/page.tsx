/**
 * Страница загрузки аудио файла
 */
"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function UploadPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [language, setLanguage] = useState("ru")
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      toast({
        title: "Ошибка",
        description: "Выберите файл для загрузки",
        variant: "destructive",
      })
      return
    }

    setUploading(true)

    try {
      const call = await api.uploadCall(file, language)

      toast({
        title: "Файл загружен",
        description: "Транскрипция началась. Вы получите уведомление о готовности.",
      })

      router.push(`/calls/${call.id}`)
    } catch (error) {
      toast({
        title: "Ошибка загрузки",
        description: "Не удалось загрузить файл. Попробуйте еще раз.",
        variant: "destructive",
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Загрузить звонок</h1>
          <p className="text-muted-foreground">Загрузите аудио файл для транскрипции и анализа</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Выбор файла</CardTitle>
            <CardDescription>
              Поддерживаемые форматы: MP3, WAV, OGG, M4A, FLAC. Максимальный размер: 100MB
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Drag & Drop зона */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".mp3,.wav,.ogg,.m4a,.flac,audio/*"
                  onChange={handleFileChange}
                />

                {file ? (
                  <div className="space-y-2">
                    <p className="text-lg font-medium">✅ {file.name}</p>
                    <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <Button type="button" variant="outline" onClick={() => setFile(null)}>
                      Выбрать другой файл
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-lg font-medium">Перетащите файл сюда</p>
                    <p className="text-sm text-muted-foreground">или</p>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => document.getElementById("file-upload")?.click()}
                    >
                      Выбрать файл
                    </Button>
                  </div>
                )}
              </div>

              {/* Выбор языка */}
              <div className="space-y-2">
                <Label htmlFor="language">Язык аудио</Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ru">Русский</SelectItem>
                    <SelectItem value="en">Английский</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Кнопка загрузки */}
              <div className="flex gap-4">
                <Button type="submit" className="flex-1" disabled={!file || uploading}>
                  {uploading ? "Загрузка..." : "Загрузить и обработать"}
                </Button>
                <Button type="button" variant="outline" onClick={() => router.push("/calls")}>
                  Отмена
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Информационные карточки */}
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Что происходит дальше?</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>1. Файл загружается на сервер</p>
              <p>2. Запускается транскрипция через Whisper AI</p>
              <p>3. Текст анализируется с помощью NLP</p>
              <p>4. Вы получаете результаты в реальном времени</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Результаты анализа</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>• Полная транскрипция текста</p>
              <p>• Ключевые слова и фразы</p>
              <p>• Категория звонка</p>
              <p>• Анализ тональности</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
