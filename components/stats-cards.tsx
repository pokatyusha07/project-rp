/**
 * Компонент карточек со статистикой
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Statistics } from "@/lib/api"

interface StatsCardsProps {
  stats: Statistics
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: "Всего звонков",
      value: stats.total_calls,
      icon: "📞",
      description: `${stats.recent_calls} за последние 30 дней`,
    },
    {
      title: "Завершено",
      value: stats.completed_calls,
      icon: "✅",
      description: `${Math.round((stats.completed_calls / stats.total_calls) * 100)}% от общего числа`,
    },
    {
      title: "В обработке",
      value: stats.pending_calls,
      icon: "⏳",
      description: "Ожидают транскрипции",
    },
    {
      title: "Средняя длительность",
      value: `${Math.round(stats.average_duration)}с`,
      icon: "⏱",
      description: `Общая: ${Math.round(stats.total_duration / 60)}мин`,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
            <span className="text-2xl">{card.icon}</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
