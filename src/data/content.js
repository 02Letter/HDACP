import manualPapers from './publications.json'
import manualNews from './news.json'
import autoPapers from './auto-publications.json'

export const dateValue = value => Date.parse(String(value).length === 4 ? `${value}-01-01` : value) || 0
export const newsData = manualNews

const venueLabels = {
  'ACM International Conference on Supercomputing (ICS)': 'ICS',
  'Proceedings of the International Conference on Parallel Processing': 'ICPP',
  'IEEE International Conference on Acoustics Speech and Signal Processing': 'ICASSP',
  'International Conference on Multimedia Retrieval': 'ICMR',
  'IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems': 'IEEE TCAD',
  'IEEE Transactions on Geoscience and Remote Sensing': 'IEEE TGRS',
  'IEEE Transactions on Network Science and Engineering': 'IEEE TNSE',
  'IEEE Transactions on Vehicular Technology': 'IEEE TVT',
  'Conference proceedings/Conference proceedings - IEEE International Conference on Systems, Man, and Cybernetics': 'IEEE SMC',
  'IEEE Information Technology and Mechatronics Engineering Conference (ITOEC)': 'ITOEC',
  'International Conference on Big Data, Artificial Intelligence and Risk Management (ICBAR)': 'ICBAR',
  'International Conference on Neural Networks, Information and Communication Engineering (NNICE)': 'NNICE',
  'Lecture notes in computer science': 'LNCS',
  'Lecture notes in electrical engineering': 'LNEE'
}

const presentation = paper => ({
  ...paper,
  displayTitle: paper.title || paper.content.replace(/<[^>]*>/g, '').replace(/^\[.*?\]\s*/, '').trim(),
  displayVenue: venueLabels[paper.venue] || paper.venue || paper.content?.match(/^\[(.*?)\]/)?.[1] || ''
})

const groups = new Map(manualPapers.map(group => [group.year, { ...group, items: [...group.items] }]))
for (const paper of autoPapers) {
  if (!groups.has(paper.year)) groups.set(paper.year, { year: paper.year, items: [] })
  groups.get(paper.year).items.push({ ...paper, content: paper.title, automated: true })
}
export const papersData = [...groups.values()].sort((a, b) => Number(b.year) - Number(a.year))
  .map(group => ({ ...group, items: group.items.sort((a, b) => dateValue(b.date || group.year) - dateValue(a.date || group.year)).map(presentation) }))
