import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('tma_token') || null,
    user: JSON.parse(localStorage.getItem('tma_user') || 'null'),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    role: (state) => (state.user ? state.user.role : null),
  },
  actions: {
    async login(email, password, role) {
      const res = await api.post('/auth/login', { email, password, role })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('tma_token', this.token)
      localStorage.setItem('tma_user', JSON.stringify(this.user))
      return this.user
    },
    async register(payload) {
      return api.post('/auth/register', payload)
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
    },
  },
})
