/**
 * WebSocket клиент для real-time обновлений
 */

type TranscriptionCallback = (data: any) => void

/**
 * Класс для управления WebSocket соединением
 */
class WebSocketClient {
  private ws: WebSocket | null = null
  private callbacks: Map<string, TranscriptionCallback[]> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  /**
   * Подключается к WebSocket для отслеживания транскрипции
   */
  connectToCall(callId: string, token: string): void {
    const wsUrl = "ws://localhost:8000"
    const url = `${wsUrl}/ws/transcription/${callId}/?token=${token}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log(`[WebSocket] Подключено к звонку ${callId}`)
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleMessage(data)
    }

    this.ws.onerror = (error) => {
      console.error("[WebSocket] Ошибка:", error)
    }

    this.ws.onclose = () => {
      console.log("[WebSocket] Соединение закрыто")
      this.attemptReconnect(callId, token)
    }
  }

  /**
   * Обрабатывает входящие сообщения
   */
  private handleMessage(data: any): void {
    const { type } = data
    const callbacks = this.callbacks.get(type) || []

    callbacks.forEach((callback) => callback(data))
  }

  /**
   * Подписывается на события
   */
  on(event: string, callback: TranscriptionCallback): void {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, [])
    }
    this.callbacks.get(event)!.push(callback)
  }

  /**
   * Отписывается от событий
   */
  off(event: string, callback: TranscriptionCallback): void {
    const callbacks = this.callbacks.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * Отправляет ping для поддержания соединения
   */
  sendPing(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "ping" }))
    }
  }

  /**
   * Пытается переподключиться
   */
  private attemptReconnect(callId: string, token: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`[WebSocket] Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)

      setTimeout(() => {
        this.connectToCall(callId, token)
      }, 2000 * this.reconnectAttempts)
    }
  }

  /**
   * Закрывает соединение
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.callbacks.clear()
  }
}

export const wsClient = new WebSocketClient()
