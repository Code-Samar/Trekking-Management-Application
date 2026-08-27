<template>
  <AppLayout>
    <div class="page-header"><div class="page-kicker">Your adventure hub</div><h3 class="fw-bold mb-1">Welcome, {{ auth.user?.name }}!</h3><p class="text-muted mb-0">Discover your next trail and keep your bookings organized.</p></div>

    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-semibold mb-0">Available Treks</h5>
      <router-link :to="{ name: 'user-treks' }" class="small">Browse All &rarr;</router-link>
    </div>
    <div class="row g-3 mb-4">
      <div class="col-md-4" v-for="t in data.available_treks.slice(0,3)" :key="t.id">
        <div class="card trek-card h-100">
          <div class="trek-cover"></div><div class="card-body">
            <h6 class="fw-bold">{{ t.name }}</h6>
            <div class="trek-meta mb-2"><span><i class="bi bi-geo-alt-fill me-1"></i>{{ t.location }}</span><span><i class="bi bi-clock me-1"></i>{{ t.duration_days }} days</span></div>
            <p class="small mb-2"><span class="badge bg-light text-dark border">{{ t.difficulty }}</span></p>
            <p class="small mb-2">Slots Left: <strong>{{ t.available_slots }}</strong></p>
            <button class="btn btn-sm btn-primary w-100" @click="book(t)" :disabled="t.available_slots === 0">
              {{ t.available_slots === 0 ? 'Not Available' : 'Book Now' }}
            </button>
          </div>
        </div>
      </div>
      <div class="col-12" v-if="!data.available_treks.length">
        <p class="text-muted">No open treks right now. Check back soon.</p>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-semibold d-flex justify-content-between">
        My Bookings
        <router-link :to="{ name: 'user-history' }" class="small">View All Bookings &rarr;</router-link>
      </div>
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>Trek Name</th><th>Booking Date</th><th>Trek Dates</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="b in data.my_bookings" :key="b.id">
              <td>{{ b.trek_name }}</td>
              <td>{{ formatDate(b.booking_date) }}</td>
              <td>{{ b.start_date }} → {{ b.end_date }}</td>
              <td><span class="badge" :class="`badge-status-${b.status}`">{{ b.status }}</span></td>
              <td>
                <button v-if="b.status === 'Booked'" class="btn btn-sm btn-outline-danger" @click="cancel(b)">Cancel</button>
              </td>
            </tr>
            <tr v-if="!data.my_bookings.length"><td colspan="5" class="text-center text-muted py-4">No bookings yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'
import { useAuthStore } from '../../store/auth'

const auth = useAuthStore()
const data = reactive({ available_treks: [], my_bookings: [] })

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

async function loadDashboard() {
  const res = await api.get('/user/dashboard')
  Object.assign(data, res.data)
}

async function book(t) {
  try {
    await api.post(`/user/treks/${t.id}/book`)
    await loadDashboard()
  } catch (err) {
    alert(err.response?.data?.error || 'Could not book this trek.')
  }
}

async function cancel(b) {
  if (!confirm(`Cancel your booking for "${b.trek_name}"?`)) return
  await api.put(`/user/bookings/${b.id}/cancel`)
  await loadDashboard()
}

onMounted(loadDashboard)
</script>
