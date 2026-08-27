<template>
  <AppLayout>
    <div class="page-header"><div class="page-kicker">Staff workspace</div><h3 class="fw-bold mb-1">My Dashboard</h3><p class="text-muted mb-0">Manage assigned treks and keep participants moving safely.</p></div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card card-stat p-3">
          <div class="stat-label">Assigned Treks</div><div class="stat-value">{{ data.assigned_treks }}</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card card-stat p-3">
          <div class="stat-label">Total Participants</div><div class="stat-value">{{ data.total_participants }}</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card card-stat p-3">
          <div class="stat-label">Ongoing Treks</div><div class="stat-value">{{ data.ongoing_treks }}</div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-semibold">My Assigned Treks</div>
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>Trek Name</th><th>Location</th><th>Dates</th><th>Slots</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in data.treks" :key="t.id">
              <td>{{ t.name }}</td>
              <td>{{ t.location }}</td>
              <td>{{ t.start_date }} → {{ t.end_date }}</td>
              <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
              <td><span class="badge" :class="`badge-status-${t.status}`">{{ t.status }}</span></td>
              <td>
                <router-link :to="{ name: 'staff-trek-manage', params: { id: t.id } }" class="btn btn-sm btn-primary">
                  {{ t.status === 'Completed' ? 'View' : 'Manage' }}
                </router-link>
              </td>
            </tr>
            <tr v-if="!data.treks?.length"><td colspan="6" class="text-center text-muted py-4">No treks assigned yet.</td></tr>
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

const data = reactive({ assigned_treks: 0, total_participants: 0, ongoing_treks: 0, treks: [] })

onMounted(async () => {
  const res = await api.get('/staff/dashboard')
  Object.assign(data, res.data)
})
</script>
