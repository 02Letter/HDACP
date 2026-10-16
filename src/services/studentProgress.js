// All visitors use the same academic calendar, regardless of their local timezone.
const calendar = new Intl.DateTimeFormat('en-US', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: 'numeric'
})
const gradeNames = {
  master: ['研一', '研二', '研三'],
  undergraduate: ['大一', '大二', '大三', '大四']
}

export function academicYear(date = new Date()) {
  const parts = Object.fromEntries(calendar.formatToParts(date).map(p => [p.type, p.value]))
  return Number(parts.year) - (Number(parts.month) < 9 ? 1 : 0)
}

export function studentProgress(student, date = new Date()) {
  // A “届” year is a graduation year; it must never become an enrollment year.
  const cohort = Number(student.cohortYear) || Number(student.year?.match(/^(\d{4})(?:级|[-–]present)/)?.[1])
  if (student.status !== 'current' || !cohort) return { ...student }

  const year = academicYear(date)
  const grade = year - cohort + 1
  // Only the confirmed three-year master's program has an automatic default.
  // Other programs can opt in with an explicit graduationYear.
  const graduationYear = Number(student.graduationYear) || (student.degree === 'master' ? cohort + 3 : 0)
  if (graduationYear && year >= graduationYear) {
    return { ...student, status: 'graduated', year: `${cohort}级毕业生` }
  }

  const gradeName = grade > 0
    ? gradeNames[student.degree]?.[grade - 1] || (student.degree === 'phd' ? `博士${grade}年级` : '')
    : ''
  return { ...student, year: `${cohort}级${gradeName ? ` · ${gradeName}` : ''}` }
}
