<template>
  <AppLayout>
    <h3 class="fw-bold mb-3">Reports &amp; Trekking Statistics</h3>
    <p class="text-muted">Trek-wise booking summary, most popular treks first.</p>
    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>Trek</th><th>Location</th><th>Status</th><th>Slots (Available/Total)</th><th>Bookings</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in rows" :key="r.trek_id">
              <td>{{ r.trek_name }}</td>
              <td>{{ r.location }}</td>
              <td><span class="badge" :class="`badge-status-${r.status}`">{{ r.status }}</span></td>
              <td>{{ r.available_slots }} / {{ r.total_slots }}</td>
              <td><strong>{{ r.bookings }}</strong></td>
            </tr>
            <tr v-if="!rows.length"><td colspan="5" class="text-center text-muted py-4">No data yet.</td></tr>
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

const rows = ref([])

onMounted(async () => {
  const res = await api.get('/admin/reports/summary')
  rows.value = res.data
})
</script>
