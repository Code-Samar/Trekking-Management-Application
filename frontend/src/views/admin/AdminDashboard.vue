<template>
  <AppLayout>
    <div class="page-header"><div class="page-kicker">Overview</div><h3 class="fw-bold mb-1">Dashboard</h3><p class="text-muted mb-0">A quick view of your trekking operations.</p></div>

    <div class="row g-3 mb-4">
      <div class="col-md-3" v-for="s in stats" :key="s.label">
        <div class="card card-stat p-3">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <div class="stat-label">{{ s.label }}</div>
              <div class="stat-value">{{ s.value }}</div>
            </div>
            <span class="stat-icon"><i :class="s.icon"></i></span>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-semibold d-flex justify-content-between">
        Recent Bookings
        <router-link :to="{name: 'admin-bookings'}" class="small">View All Bookings &rarr;</router-link>
      </div>
      <div class="table-responsive">
        <table class="table mb-0 align-middle">
          <thead class="table-light">
            <tr><th>Booking ID</th><th>User</th><th>Trek</th><th>Booking Date</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="b in data.recent_bookings" :key="b.id">
              <td>#{{ b.id }}</td>
              <td>{{ b.user_name }}</td>
              <td>{{ b.trek_name }}</td>
              <td>{{ formatDate(b.booking_date) }}</td>
              <td><span class="badge" :class="`badge-status-${b.status}`">{{ b.status }}</span></td>
            </tr>
            <tr v-if="!data.recent_bookings?.length"><td colspan="5" class="text-center text-muted py-3">No bookings yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, computed } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const data = reactive({
  total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0, recent_bookings: [],
})

const stats = computed(() => [
  { label: 'Total Treks', value: data.total_treks, icon: 'bi bi-map' },
  { label: 'Total Users (Trekkers)', value: data.total_users, icon: 'bi bi-people' },
  { label: 'Total Trekking Staff', value: data.total_staff, icon: 'bi bi-person-badge' },
  { label: 'Total Bookings', value: data.total_bookings, icon: 'bi bi-calendar-check' },
])

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString()
}

onMounted(async () => {
  const res = await api.get('/admin/dashboard')
  Object.assign(data, res.data)
})
</script>
