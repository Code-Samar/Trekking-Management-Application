<template>
  <AppLayout>
    <h3 class="fw-bold mb-3">All Bookings</h3>
    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>Booking ID</th><th>User</th><th>Trek</th><th>Location</th><th>Booking Date</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="b in bookings" :key="b.id">
              <td>#{{ b.id }}</td>
              <td>{{ b.user_name }}</td>
              <td>{{ b.trek_name }}</td>
              <td>{{ b.location }}</td>
              <td>{{ formatDate(b.booking_date) }}</td>
              <td><span class="badge" :class="`badge-status-${b.status}`">{{ b.status }}</span></td>
            </tr>
            <tr v-if="!bookings.length"><td colspan="6" class="text-center text-muted py-4">No bookings yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const bookings = ref([])
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

onMounted(async () => {
  const res = await api.get('/admin/bookings')
  bookings.value = res.data
})
</script>
