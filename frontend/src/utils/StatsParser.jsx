export function parseStatsData(stats, namesKey = "radio_names", includeDistinctSongs = false) {
  const {
    daily_counts,
    distinct_songs_daily_counts,
    weekday_counts,
    hourly_counts,
    time_of_day_counts,
  } = stats;

  const categories = Object.keys(Object.values(daily_counts || {})[0] || {});
  const series = [
    ...Object.entries(daily_counts || {}).map(([id, counts]) => ({
      name: stats[namesKey]?.[id] || "Plays",
      data: Object.entries(counts).map(([date, value]) => ({ x: date, y: value })),
    })),
    ...(includeDistinctSongs
      ? Object.entries(distinct_songs_daily_counts || {}).map(([id, counts]) => ({
          name: stats[namesKey]?.[id] || "Different Songs",
          data: Object.entries(counts).map(([date, value]) => ({ x: date, y: value })),
        }))
      : []),
  ];

  const weekdayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const weekdaySeries = Object.entries(weekday_counts || {}).map(([id, dayCounts]) => ({
    name: stats[namesKey]?.[id] || stats["name"],
    data: weekdayOrder.map((day) => dayCounts?.[day] || 0),
  }));

  const hourlyOrder = Array.from({ length: 24 }, (_, i) => i);
  const hourlySeries = Object.entries(hourly_counts || {}).map(([id, hourCounts]) => ({
    name: stats[namesKey]?.[id] || stats["name"],
    data: hourlyOrder.map((hour) => hourCounts?.[hour] || 0),
  }));

  const timeOfDayOrder = ["dawn", "morning", "afternoon", "night"];
  const timeOfDaySeries = timeOfDayOrder.map((time) => time_of_day_counts?.[time] || 0);

  return {
    categories,
    series,
    weekdaySeries,
    hourlySeries,
    timeOfDaySeries,
  };
}