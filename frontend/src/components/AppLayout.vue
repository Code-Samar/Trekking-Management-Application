<template>
  <div class="app-shell">
    <nav class="navbar topbar px-3 px-lg-4 py-2">
      <div class="container-fluid px-0">
        <div class="d-flex align-items-center gap-2">
          <span class="brand-mark"><i class="bi bi-signpost-split-fill"></i></span>
          <span class="navbar-brand mb-0">Trek<span class="text-primary-tma">Flow</span></span>
        </div>
        <div class="d-flex align-items-center gap-2">
          <div class="user-chip">
            <span class="user-avatar"><i class="bi bi-person-fill"></i></span>
            <span class="user-name"><strong class="d-block small">{{ auth.user?.name }}</strong><small class="text-muted">{{ roleLabel }}</small></span>
          </div>
          <button class="btn btn-sm btn-outline-danger" @click="handleLogout" title="Logout">
            <i class="bi bi-box-arrow-right"></i><span class="d-none d-sm-inline ms-1">Logout</span>
          </button>
        </div>
      </div>
    </nav>

    <div class="container-fluid px-0">
      <div class="row g-0">
        <aside class="col-lg-2 sidebar">
          <div class="sidebar-label">Workspace</div>
          <ul class="nav nav-pills flex-column">
            <li class="nav-item" v-for="item in navItems" :key="item.name">
              <router-link class="nav-link" :to="{ name: item.name }" active-class="active">
                <i :class="item.icon" class="me-2"></i>{{ item.label }}
              </router-link>
            </li>
          </ul>
        </aside>
        <main class="col-lg-10 main-content p-3 p-md-4 p-xl-5">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const roleLabel = computed(() => auth.role === 'trekker' ? 'Trekker' : auth.role === 'staff' ? 'Trek Staff' : 'Administrator')
const navMap = {
  admin: [
    { name: 'admin-dashboard', label: 'Dashboard', icon: 'bi bi-grid-1x2-fill' },
    { name: 'admin-treks', label: 'Treks', icon: 'bi bi-map' },
    { name: 'admin-staff', label: 'Trekking Staff', icon: 'bi bi-person-badge' },
    { name: 'admin-users', label: 'Users', icon: 'bi bi-people' },
    { name: 'admin-bookings', label: 'Bookings', icon: 'bi bi-calendar2-check' },
    { name: 'admin-reports', label: 'Reports', icon: 'bi bi-bar-chart-line' },
  ],
  staff: [{ name: 'staff-dashboard', label: 'Dashboard', icon: 'bi bi-grid-1x2-fill' }],
  trekker: [
    { name: 'user-dashboard', label: 'Dashboard', icon: 'bi bi-grid-1x2-fill' },
    { name: 'user-treks', label: 'Browse Treks', icon: 'bi bi-compass' },
    { name: 'user-history', label: 'My Bookings', icon: 'bi bi-clock-history' },
    { name: 'user-profile', label: 'Profile', icon: 'bi bi-person' },
  ],
}
const navItems = computed(() => navMap[auth.role] || [])
function handleLogout() { auth.logout(); router.push({ name: 'login' }) }
</script>
