<template>
  <AppLayout>
    <router-link :to="{ name: 'staff-dashboard' }" class="small d-inline-block mb-2">&larr; Back to My Treks</router-link>
    <div class="row">
      <div class="col-md-5">
        <div class="card border-0 shadow-sm p-3 mb-3">
          <h5 class="fw-bold">Trek Details</h5>
          <p class="mb-1"><strong>{{ trek.name }}</strong></p>
          <p class="text-muted mb-1">{{ trek.location }} • {{ trek.difficulty }}</p>
          <p class="mb-1">Duration: {{ trek.duration_days }} days</p>
          <p class="mb-1">Start: {{ trek.start_date }} &nbsp; End: {{ trek.end_date }}</p>
          <p class="mb-3">Total Slots: {{ trek.total_slots }}</p>

          <div v-if="msg" class="alert" :class="msgType === 'error' ? 'alert-danger' : 'alert-success'">{{ msg }}</div>

          <div class="mb-2">
            <label class="form-label">Available Slots</label>
            <input v-model.number="editable.available_slots" type="number" min="0" :max="trek.total_slots" class="form-control" :disabled="trek.status === 'Completed'" />
          </div>
          <div class="mb-3">
            <label class="form-label">Status</label>
            <select v-model="editable.status" class="form-select" :disabled="trek.status === 'Completed'">
              <option>Pending</option>
              <option>Approved</option>
              <option>Open</option>
              <option>Closed</option>
              <option>Completed</option>
            </select>
          </div>

          <button class="btn btn-primary mb-2" @click="updateTrek" :disabled="trek.status === 'Completed'">Update Trek</button>
          <button class="btn btn-outline-success" @click="markCompleted" v-if="trek.status !== 'Completed'">Mark as Completed</button>
        </div>
      </div>

      <div class="col-md-7">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white fw-semibold">Participants ({{ participants.length }})</div>
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead class="table-light">
                <tr><th>#</th><th>Name</th><th>Email</th><th>Booking Date</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="(p, idx) in participants" :key="p.id">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ p.user_name }}</td>
                  <td>{{ p.user_email || '—' }}</td>
                  <td>{{ formatDate(p.booking_date) }}</td>
                  <td><span class="badge" :class="`badge-status-${p.status}`">{{ p.status }}</span></td>
                </tr>
                <tr v-if="!participants.length"><td colspan="5" class="text-center text-muted py-4">No participants yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const route = useRoute()
const trek = reactive({})
const editable = reactive({ available_slots: 0, status: 'Pending' })
const participants = ref([])
const msg = ref('')
const msgType = ref('success')

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

async function loadTrek() {
  const res = await api.get('/staff/treks')
  const found = res.data.find(t => String(t.id) === String(route.params.id))
  if (found) {
    Object.assign(trek, found)
    editable.available_slots = found.available_slots
    editable.status = found.status
  }
}

async function loadParticipants() {
  const res = await api.get(`/staff/treks/${route.params.id}/participants`)
  participants.value = res.data
}

async function updateTrek() {
  msg.value = ''
  try {
    const res = await api.put(`/staff/treks/${route.params.id}`, editable)
    Object.assign(trek, res.data)
    msg.value = 'Trek updated successfully.'
    msgType.value = 'success'
  } catch (err) {
    msg.value = err.response?.data?.error || 'Could not update trek.'
    msgType.value = 'error'
  }
}

async function markCompleted() {
  if (!confirm('Mark this trek as completed? This will finalize all active bookings.')) return
  const res = await api.put(`/staff/treks/${route.params.id}/complete`)
  Object.assign(trek, res.data)
  editable.status = trek.status
  await loadParticipants()
}

onMounted(async () => {
  await loadTrek()
  await loadParticipants()
})
</script>
