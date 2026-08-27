<template>
  <AppLayout>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="fw-bold mb-0">Treks</h3>
      <button class="btn btn-primary" @click="openCreate">
        <i class="bi bi-plus-lg me-1"></i>Add New Trek
      </button>
    </div>

    <div class="mb-3">
      <input v-model="search" @input="debouncedSearch" class="form-control" placeholder="Search treks by name or location...">
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>ID</th><th>Name</th><th>Location</th><th>Difficulty</th><th>Slots</th><th>Staff</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in treks" :key="t.id">
              <td>{{ t.id }}</td>
              <td>{{ t.name }}</td>
              <td>{{ t.location }}</td>
              <td>{{ t.difficulty }}</td>
              <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
              <td>{{ t.assigned_staff_name || '—' }}</td>
              <td><span class="badge" :class="`badge-status-${t.status}`">{{ t.status }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-1" @click="openEdit(t)"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger" @click="removeTrek(t)"><i class="bi bi-trash"></i></button>
              </td>
            </tr>
            <tr v-if="!treks.length"><td colspan="8" class="text-center text-muted py-4">No treks found.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" tabindex="-1" ref="modalEl">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ form.id ? 'Edit Trek' : 'Create New Trek' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveTrek">
            <div class="modal-body">
              <div class="mb-2">
                <label class="form-label">Trek Name</label>
                <input v-model="form.name" class="form-control" required />
              </div>
              <div class="row">
                <div class="col-md-6 mb-2">
                  <label class="form-label">Location</label>
                  <input v-model="form.location" class="form-control" required />
                </div>
                <div class="col-md-6 mb-2">
                  <label class="form-label">Difficulty</label>
                  <select v-model="form.difficulty" class="form-select" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-2">
                  <label class="form-label">Duration (days)</label>
                  <input v-model.number="form.duration_days" type="number" min="1" class="form-control" required />
                </div>
                <div class="col-md-6 mb-2">
                  <label class="form-label">Total Slots</label>
                  <input v-model.number="form.total_slots" type="number" min="1" class="form-control" required />
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-2">
                  <label class="form-label">Start Date</label>
                  <input v-model="form.start_date" type="date" class="form-control" />
                </div>
                <div class="col-md-6 mb-2">
                  <label class="form-label">End Date</label>
                  <input v-model="form.end_date" type="date" class="form-control" />
                </div>
              </div>
              <div class="mb-2">
                <label class="form-label">Assign Staff</label>
                <select v-model="form.assigned_staff_id" class="form-select">
                  <option :value="null">— Unassigned —</option>
                  <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>
              <div class="mb-2">
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-select">
                  <option>Pending</option>
                  <option>Approved</option>
                  <option>Open</option>
                  <option>Closed</option>
                  <option>Completed</option>
                </select>
              </div>
              <div class="mb-2">
                <label class="form-label">Description</label>
                <textarea v-model="form.description" class="form-control" rows="2"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">{{ form.id ? 'Update Trek' : 'Create Trek' }}</button>
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

const treks = ref([])
const staffList = ref([])
const search = ref('')
const errorMsg = ref('')
const modalEl = ref(null)
let modalInstance = null

const emptyForm = () => ({
  id: null, name: '', location: '', difficulty: 'Moderate', duration_days: 5,
  total_slots: 10, start_date: '', end_date: '', assigned_staff_id: null,
  status: 'Pending', description: '',
})
const form = reactive(emptyForm())

async function loadTreks() {
  const res = await api.get('/admin/treks', { params: { q: search.value } })
  treks.value = res.data
}

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadTreks, 300)
}

async function loadStaff() {
  const res = await api.get('/admin/staff')
  staffList.value = res.data
}

function openCreate() {
  Object.assign(form, emptyForm())
  modalInstance.show()
}

function openEdit(t) {
  Object.assign(form, {
    id: t.id, name: t.name, location: t.location, difficulty: t.difficulty,
    duration_days: t.duration_days, total_slots: t.total_slots,
    start_date: t.start_date || '', end_date: t.end_date || '',
    assigned_staff_id: t.assigned_staff_id, status: t.status, description: t.description || '',
  })
  modalInstance.show()
}

async function saveTrek() {
  errorMsg.value = ''
  try {
    if (form.id) {
      await api.put(`/admin/treks/${form.id}`, form)
    } else {
      await api.post('/admin/treks', form)
    }
    modalInstance.hide()
    await loadTreks()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Could not save trek.'
  }
}

async function removeTrek(t) {
  if (!confirm(`Delete trek "${t.name}"? This cannot be undone.`)) return
  try {
    await api.delete(`/admin/treks/${t.id}`)
    await loadTreks()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Could not delete trek.'
  }
}

onMounted(async () => {
  modalInstance = new Modal(modalEl.value)
  await Promise.all([loadTreks(), loadStaff()])
})
</script>
