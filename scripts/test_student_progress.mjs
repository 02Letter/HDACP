import assert from 'node:assert/strict'
import { test } from 'node:test'
import { academicYear, studentProgress } from '../src/services/studentProgress.js'

const master = cohort => ({ name: '学生', status: 'current', degree: 'master', year: `${cohort}级`, photo: 'photo.jpg' })
const now = new Date('2026-10-16T00:00:00Z')

test('Beijing September rollover ignores the visitor timezone', () => {
  const before = new Date('2027-08-31T15:59:59Z')
  const after = new Date('2027-08-31T16:00:00Z')
  assert.equal(academicYear(before), 2026)
  assert.equal(academicYear(after), 2027)
  assert.equal(studentProgress(master(2024), before).year, '2024级 · 研三')
  assert.equal(studentProgress(master(2024), before).status, 'current')
  assert.equal(studentProgress(master(2024), after).status, 'graduated')
  assert.equal(studentProgress(master(2024), after).year, '2024级毕业生')
  assert.equal(studentProgress(master(2025), before).year, '2025级 · 研二')
  assert.equal(studentProgress(master(2025), after).year, '2025级 · 研三')
})

test('current cohorts advance and legacy present dates graduate', () => {
  assert.equal(studentProgress(master(2024), now).year, '2024级 · 研三')
  assert.equal(studentProgress(master(2025), now).year, '2025级 · 研二')
  assert.equal(studentProgress(master(2026), now).year, '2026级 · 研一')
  for (const cohort of [2020, 2021, 2022, 2023]) {
    assert.equal(studentProgress({ ...master(cohort), year: `${cohort}-present` }, now).status, 'graduated')
  }
})

test('manual alumni, destinations and source records are preserved', () => {
  const alumnus = { ...master(2023), status: 'graduated', year: '2023级毕业生', research: '天津大学' }
  assert.deepEqual(studentProgress(alumnus, now), alumnus)
  assert.deepEqual(studentProgress({ ...alumnus, year: '2020届毕业生（本科）' }, now), { ...alumnus, year: '2020届毕业生（本科）' })
  const source = master(2024)
  studentProgress(source, new Date('2028-10-01T00:00:00Z'))
  assert.equal(source.status, 'current')
  assert.equal(source.year, '2024级')
})

test('unknown cohorts and doctoral graduation dates are not guessed', () => {
  const unknown = { status: 'current', degree: 'master', year: '' }
  assert.deepEqual(studentProgress(unknown, now), unknown)
  const phd = { ...master(2026), degree: 'phd' }
  assert.equal(studentProgress(phd, now).year, '2026级 · 博士1年级')
  assert.equal(studentProgress(phd, new Date('2032-10-01T00:00:00Z')).status, 'current')
  assert.equal(studentProgress({ ...phd, graduationYear: 2030 }, new Date('2030-09-01T00:00:00Z')).status, 'graduated')
})

test('an explicit postponed graduation overrides the default master duration', () => {
  const postponed = { ...master(2023), graduationYear: 2027 }
  assert.equal(studentProgress(postponed, now).status, 'current')
  assert.equal(studentProgress(postponed, new Date('2027-09-01T00:00:00Z')).status, 'graduated')
})
