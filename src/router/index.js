import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/research',
      name: 'research',
      component: () => import('../views/ResearchView.vue')
    },
    {
      path: '/research/:id',
      name: 'research-detail',
      component: () => import('../views/ResearchView.vue')
    },
    {
      path: '/team',
      name: 'team',
      component: () => import('../views/TeamView.vue')
    },
    {
      path: '/teacher/:id',
      name: 'teacher-profile',
      component: () => import('../views/TeacherProfileView.vue')
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('../views/NewsView.vue')
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('../views/ProjectsView.vue')
    },
    {
      path: '/papers',
      name: 'papers',
      component: () => import('../views/PapersView.vue')
    },
    {
      path: '/life',
      name: 'life',
      component: () => import('../views/LifeView.vue')
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/ContactView.vue')
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

export default router
