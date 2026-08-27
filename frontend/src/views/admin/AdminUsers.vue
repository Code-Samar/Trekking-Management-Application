<template>
  <AppLayout>
    <h3 class="fw-bold mb-3">Users (Trekkers)</h3>

    <div class="mb-3">
      <input v-model="search" @input="debouncedSearch" class="form-control" placeholder="Search users...">
    </div>

    <div class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>U{{ String(u.id).padStart(3,'0') }}</td>
              <td>{{ u.name }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.contact_number || '—' }}</td>
              <td><span :class="u.status === 'active' ? 'badge bg-success' : 'badge bg-danger'">{{ u.status }}</span></td>
              <td>
                <button v-if="u.status === 'active'" class="btn btn-sm btn-outline-danger" @click="toggleStatus(u, 'blacklisted')">Blacklist</button>
                <button v-else class="btn btn-sm btn-outline-success" @click="toggleStatus(u, 'active')">Whitelist</button>
              </td>
            </tr>
            <tr v-if="!users.length"><td colspan="6" class="text-center text-muted py-4">No users found.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="alert alert-info small mt-3"><i class="bi bi-info-circle me-1"></i>Blacklisted users cannot login or book treks.</div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'

const users = ref([])
const search = ref('')

async function loadUsers() {
  const res = await api.get('/admin/users', { params: { q: search.value } })
  users.value = res.data
}

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadUsers, 300)
}

async function toggleStatus(u, status) {
  await api.put(`/admin/users/${u.id}/status`, { status })
  await loadUsers()
}

onMounted(loadUsers)
</script>
