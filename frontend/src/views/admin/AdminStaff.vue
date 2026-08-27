<template>
  <AppLayout>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="fw-bold mb-0">Trekking Staff</h3>
      <button class="btn btn-primary" @click="openCreate"><i class="bi bi-plus-lg me-1"></i>Create New Trekking Staff</button>
    </div>

    <div class="mb-3">
      <input v-model="search" @input="debouncedSearch" class="form-control" placeholder="Search trekking staff...">
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in staffList" :key="s.id">
              <td>TS{{ String(s.id).padStart(3,'0') }}</td>
              <td>{{ s.name }}</td>
              <td>{{ s.email }}</td>
              <td>{{ s.contact_number || '—' }}</td>
              <td><span :class="s.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">{{ s.status }}</span></td>
              <td>
                <button v-if="s.status === 'active'" class="btn btn-sm btn-outline-danger" @click="toggleStatus(s, 'blacklisted')">Blacklist</button>
                <button v-else class="btn btn-sm btn-outline-success" @click="toggleStatus(s, 'active')">Whitelist</button>
              </td>
            </tr>
            <tr v-if="!staffList.length"><td colspan="6" class="text-center text-muted py-4">No staff found.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" ref="modalEl">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Trekking Staff</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveStaff">
            <div class="modal-body">
              <div class="mb-2">
                <label class="form-label">Full Name</label>
                <input v-model="form.name" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Email Address</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Contact Number</label>
                <input v-model="form.contact_number" class="form-control" />
              </div>
              <div class="mb-2">
                <label class="form-label">Password</label>
                <input v-model="form.password" type="password" class="form-control" required minlength="6" />
              </div>
              <div class="row">
                <div class="col-md-6 mb-2">
                  <label class="form-label">Experience (years)</label>
                  <input v-model.number="form.experience_years" type="number" min="0" class="form-control" />
                </div>
                <div class="col-md-6 mb-2">
                  <label class="form-label">Specialization</label>
                  <input v-model="form.specialization" class="form-control" placeholder="e.g. High Altitude" />
                </div>
              </div>
              <div class="alert alert-info small mb-0">The staff member will receive their login credentials.</div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Create Staff</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Modal } from 'bootstrap'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const staffList = ref([])
const search = ref('')
const errorMsg = ref('')
const modalEl = ref(null)
let modalInstance = null

const form = reactive({
  name: '', email: '', contact_number: '', password: '', experience_years: null, specialization: '',
})

async function loadStaff() {
  const res = await api.get('/admin/staff', { params: { q: search.value } })
  staffList.value = res.data
}

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadStaff, 300)
}

function openCreate() {
  Object.assign(form, { name: '', email: '', contact_number: '', password: '', experience_years: null, specialization: '' })
  modalInstance.show()
}

async function saveStaff() {
  errorMsg.value = ''
  try {
    await api.post('/admin/staff', form)
    modalInstance.hide()
    await loadStaff()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Could not create staff.'
  }
}

async function toggleStatus(s, status) {
  await api.put(`/admin/staff/${s.id}/status`, { status })
  await loadStaff()
}

onMounted(async () => {
  modalInstance = new Modal(modalEl.value)
  await loadStaff()
})
</script>
