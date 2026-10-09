import manualPapers from './publications.json'
import manualNews from './news.json'
import autoPapers from './auto-publications.json'
import autoNews from './auto-news.json'

export const dateValue = value => Date.parse(String(value).length === 4 ? `${value}-01-01` : value) || 0
export const newsData = { ...manualNews, news: [...manualNews.news, ...autoNews] }

const groups = new Map(manualPapers.map(group => [group.year, { ...group, items: [...group.items] }]))
for (const paper of autoPapers) {
  if (!groups.has(paper.year)) groups.set(paper.year, { year: paper.year, items: [] })
  groups.get(paper.year).items.push({ ...paper, content: paper.title, automated: true })
}
export const papersData = [...groups.values()].sort((a, b) => Number(b.year) - Number(a.year))
  .map(group => ({ ...group, items: group.items.sort((a, b) => dateValue(b.date || group.year) - dateValue(a.date || group.year)) }))
