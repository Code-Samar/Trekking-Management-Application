<template>
  <AppLayout>
    <h3 class="fw-bold mb-3">My Profile</h3>

    <div class="card border-0 shadow-sm p-4" style="max-width: 500px;">
      <div v-if="msg" class="alert" :class="msgType === 'error' ? 'alert-danger' : 'alert-success'">{{ msg }}</div>

      <form @submit.prevent="saveProfile">
        <div class="mb-3">
          <label class="form-label">Full Name</label>
          <input v-model="form.name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Email (cannot be changed)</label>
          <input :value="form.email" class="form-control" disabled />
        </div>
        <div class="mb-3">
          <label class="form-label">Contact Number</label>
          <input v-model="form.contact_number" class="form-control" />
        </div>

        <hr>
        <p class="text-muted small">Leave password fields blank if you don't want to change it.</p>
        <div class="mb-3">
          <label class="form-label">Current Password</label>
          <input v-model="form.current_password" type="password" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">New Password</label>
          <input v-model="form.new_password" type="password" class="form-control" minlength="6" />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          Save Changes
        </button>
      </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import api from '../../api'
import { useAuthStore } from '../../store/auth'

const auth = useAuthStore()
const saving = ref(false)
const msg = ref('')
const msgType = ref('success')

const form = reactive({
  name: '', email: '', contact_number: '', current_password: '', new_password: '',
})

async function loadProfile() {
  const res = await api.get('/user/profile')
  form.name = res.data.name
  form.email = res.data.email
  form.contact_number = res.data.contact_number || ''
}

async function saveProfile() {
  saving.value = true
  msg.value = ''
  try {
    const res = await api.put('/user/profile', form)
    auth.user = res.data
    localStorage.setItem('tma_user', JSON.stringify(res.data))
    form.current_password = ''
    form.new_password = ''
    msg.value = 'Profile updated successfully.'
    msgType.value = 'success'
  } catch (err) {
    msg.value = err.response?.data?.error || 'Could not update profile.'
    msgType.value = 'error'
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>
