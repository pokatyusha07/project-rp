/**
 * API клиент для взаимодействия с Django backend
 */

const API_BASE_URL = "http://localhost:8000/api"

interface AuthTokens {
  access: string
  refresh: string
}

interface Call {
  id: string
  user_name: string
  duration: number
  status: string
  status_display: string
  language: string
  source: string
  created_at: string
  has_transcription: boolean
  has_analysis: boolean
}

interface CallDetail extends Call {
  transcription?: {
    text: string
    confidence: number
    segments: Array<{
      start: number
      end: number
      text: string
    }>
  }
  analysis?: {
    category: string
    category_display: string
    keywords: string[]
    sentiment: string
    word_frequency: Record<string, number>
    summary: string
  }
}

interface Statistics {
  total_calls: number
  completed_calls: number
  pending_calls: number
  failed_calls: number
  recent_calls: number
  total_duration: number
  average_duration: number
}

/**
 * Класс для работы с API
 */
class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_BASE_URL
  }

  /**
   * Получает токен доступа из localStorage
   */
  private getAccessToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem("access_token")
  }

  /**
   * Сохраняет токены в localStorage
   */
  private saveTokens(tokens: AuthTokens): void {
    localStorage.setItem("access_token", tokens.access)
    localStorage.setItem("refresh_token", tokens.refresh)
  }

  /**
   * Очищает токены из localStorage
   */
  private clearTokens(): void {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
  }

  /**
   * Выполняет HTTP запрос с автоматической обработкой токенов
   */
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAccessToken()

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Регистрация пользователя
   */


async register(username: string, email: string, password: string) {
    const response = await fetch("http://localhost:8000/api/users/register/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username,
            email,
            password,
            password_confirm: password, // если нужен подтверждающий пароль
        }),
    })

    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(JSON.stringify(errorData))
    }

    const data: { user: any; tokens: AuthTokens } = await response.json()
    this.saveTokens(data.tokens)
    return data.user
}

/**
 * Вход пользователя
 */
async login(username: string, password: string) {
    const response = await fetch("http://localhost:8000/api/users/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    })

    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(JSON.stringify(errorData))
    }

    const data: { user: any; tokens: AuthTokens } = await response.json()
    this.saveTokens(data.tokens)
    return data.user
}


/**
   * Выход пользователя
   */
  logout(): void {
    this.clearTokens()
  }

  /**
   * Получает профиль текущего пользователя
   */
  async getCurrentUser() {
    return this.request("/users/me/")
  }

  /**
   * Загружает аудио файл
   */
  async uploadCall(file: File, language = "ru"): Promise<CallDetail> {
    const token = this.getAccessToken()
    const formData = new FormData()
    formData.append("audio_file", file)
    formData.append("language", language)
    formData.append("source", "web")

    const response = await fetch(`${this.baseUrl}/calls/calls/upload/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error("Failed to upload file")
    }

    return response.json()
  }

  /**
   * Получает список звонков
   */
  async getCalls(page = 1): Promise<{ results: Call[]; count: number }> {
    return this.request(`/calls/calls/?page=${page}`)
  }

  /**
   * Получает детали звонка
   */
  async getCallDetail(callId: string): Promise<CallDetail> {
    return this.request(`/calls/calls/${callId}/`)
  }

  /**
   * Поиск по звонкам
   */
  async searchCalls(query: string, category?: string): Promise<Call[]> {
    let url = `/calls/calls/search/?q=${encodeURIComponent(query)}`
    if (category) {
      url += `&category=${category}`
    }
    return this.request(url)
  }

  /**
   * Получает статистику
   */
  async getStatistics(): Promise<Statistics> {
    return this.request("/analytics/stats/overview/")
  }

  /**
   * Получает статистику по категориям
   */
  async getCategoriesStats() {
    return this.request("/analytics/stats/categories/")
  }

  /**
   * Получает статистику по дням
   */
  async getDailyStats(days = 30) {
    return this.request(`/analytics/stats/daily_stats/?days=${days}`)
  }

  /**
   * Получает топ ключевых слов
   */
  async getTopKeywords(limit = 20) {
    return this.request(`/analytics/stats/top_keywords/?limit=${limit}`)
  }
}

export const api = new ApiClient()
export type { Call, CallDetail, Statistics }
