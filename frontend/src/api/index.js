import api from './client'

export const sync = () => api.post('/sync/')
export const syncStatus = () => api.get('/sync/status')

export const getAnalyticsSummary = () => api.get('/analytics/summary')
export const getAnalyticsSubjects = () => api.get('/analytics/subjects')

export const getSubjects = () => api.get('/subjects/')
export const getGrades = () => api.get('/grades/')
export const getGPA = () => api.get('/grades/gpa')
export const getAttendance = () => api.get('/attendance/')
export const getUpcomingExams = () => api.get('/exams/upcoming')
export const getAnnouncements = () => api.get('/announcements/')
