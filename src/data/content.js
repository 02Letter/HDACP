import manualPapers from './publications.json'
import manualNews from './news.json'
import autoPapers from './auto-publications.json'
import metadata from './publication-metadata.json'

export const dateValue = value => Date.parse(String(value).length === 4 ? `${value}-01-01` : value) || 0
export const newsData = manualNews

const presentation = paper => {
  const verified = metadata[paper.id]
  return { ...paper, ...verified, displayTitle: verified.title, displayVenue: verified.label }
}

// New automatic records wait for DOI, title, author and publisher venue verification.
export const verifiedAutoPapers = autoPapers.filter(paper => metadata[paper.id]).map(presentation)
const seen = new Set()
const unique = paper => {
  const key = paper.doi.toLowerCase()
  if (seen.has(key)) return false
  seen.add(key)
  return true
}
const groups = new Map(manualPapers.map(group => [group.year, {
  ...group, items: group.items.filter(paper => metadata[paper.id]).map(presentation).filter(unique)
}]))
for (const paper of verifiedAutoPapers.filter(unique)) {
  if (!groups.has(paper.year)) groups.set(paper.year, { year: paper.year, items: [] })
  groups.get(paper.year).items.push({ ...paper, content: paper.title, automated: true })
}
export const papersData = [...groups.values()].sort((a, b) => Number(b.year) - Number(a.year))
  .map(group => ({ ...group, items: group.items.sort((a, b) => dateValue(b.date || group.year) - dateValue(a.date || group.year)) }))
  .filter(group => group.items.length)
