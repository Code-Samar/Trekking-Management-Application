<template>
  <AppLayout>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="fw-bold mb-0">Trekking History</h3>
      <button class="btn btn-outline-primary" @click="exportHistory" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
        <i v-else class="bi bi-download me-1"></i>
        {{ exporting ? 'Preparing export...' : 'Export as CSV' }}
      </button>
    </div>

    <div v-if="exportMsg" class="alert alert-success">
      {{ exportMsg }} <a v-if="exportFile" :href="downloadUrl" class="alert-link">Download here</a>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>Trek Name</th><th>Trek Dates</th><th>Completed/Cancelled On</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="h in history" :key="h.id">
              <td>{{ h.trek_name }}</td>
              <td>{{ h.start_date }} → {{ h.end_date }}</td>
              <td>{{ formatDate(h.booking_date) }}</td>
              <td><span class="badge" :class="`badge-status-${h.status}`">{{ h.status }}</span></td>
            </tr>
            <tr v-if="!history.length"><td colspan="4" class="text-center text-muted py-4">No completed or cancelled treks yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="alert alert-info small mt-3"><i class="bi bi-info-circle me-1"></i>History shows all your completed and cancelled treks.</div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const history = ref([])
const exporting = ref(false)
const exportMsg = ref('')
const exportFile = ref('')

const downloadUrl = ref('')

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

async function loadHistory() {
  const res = await api.get('/user/history')
  history.value = res.data
}

async function exportHistory() {
  exporting.value = true
  exportMsg.value = ''
  exportFile.value = ''
  try {
    const res = await api.post('/user/export-history')
    const taskId = res.data.task_id
    await pollExport(taskId)
  } catch (err) {
    exportMsg.value = err.response?.data?.error || 'Could not start export.'
    exporting.value = false
  }
}

async function pollExport(taskId, attempts = 0) {
  if (attempts > 20) {
    exportMsg.value = 'Export is taking longer than expected. Please check back shortly.'
    exporting.value = false
    return
  }
  const res = await api.get(`/user/export-history/${taskId}`)
  if (res.data.state === 'SUCCESS') {
    exportFile.value = res.data.file
    downloadUrl.value = `/api/downloads/exports/${res.data.file}`
    exportMsg.value = 'Your export is ready.'
    exporting.value = false
  } else if (res.data.state === 'FAILURE') {
    exportMsg.value = 'Export failed. Please try again.'
    exporting.value = false
  } else {
    setTimeout(() => pollExport(taskId, attempts + 1), 1000)
  }
}

onMounted(loadHistory)
</script>
