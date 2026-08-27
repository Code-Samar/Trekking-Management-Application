import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue') },

  // Admin
  { path: '/admin/dashboard', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: { role: 'admin' } },
  { path: '/admin/treks', name: 'admin-treks', component: () => import('../views/admin/AdminTreks.vue'), meta: { role: 'admin' } },
  { path: '/admin/staff', name: 'admin-staff', component: () => import('../views/admin/AdminStaff.vue'), meta: { role: 'admin' } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { role: 'admin' } },
  { path: '/admin/bookings', name: 'admin-bookings', component: () => import('../views/admin/AdminBookings.vue'), meta: { role: 'admin' } },
  { path: '/admin/reports', name: 'admin-reports', component: () => import('../views/admin/AdminReports.vue'), meta: { role: 'admin' } },

  // Staff
  { path: '/staff/dashboard', name: 'staff-dashboard', component: () => import('../views/staff/StaffDashboard.vue'), meta: { role: 'staff' } },
  { path: '/staff/treks/:id', name: 'staff-trek-manage', component: () => import('../views/staff/StaffTrekManage.vue'), meta: { role: 'staff' } },

  // Trekker
  { path: '/user/dashboard', name: 'user-dashboard', component: () => import('../views/user/UserDashboard.vue'), meta: { role: 'trekker' } },
  { path: '/user/treks', name: 'user-treks', component: () => import('../views/user/UserBrowseTreks.vue'), meta: { role: 'trekker' } },
  { path: '/user/history', name: 'user-history', component: () => import('../views/user/UserHistory.vue'), meta: { role: 'trekker' } },
  { path: '/user/profile', name: 'user-profile', component: () => import('../views/user/UserProfile.vue'), meta: { role: 'trekker' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.role) {
    if (!auth.isAuthenticated) {
      return next({ name: 'login' })
    }
    if (auth.role !== to.meta.role) {
      // Logged in but wrong role -> send to their own dashboard
      return next({ name: `${auth.role === 'trekker' ? 'user' : auth.role}-dashboard` })
    }
  }

  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return next({ name: `${auth.role === 'trekker' ? 'user' : auth.role}-dashboard` })
  }

  next()
})

export default router
