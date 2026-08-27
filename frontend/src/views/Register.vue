<template>
  <div class="d-flex align-items-center justify-content-center min-vh-100 py-4" style="background-color: var(--tma-bg);">
    <div class="card shadow-sm border-0" style="max-width: 460px; width: 100%;">
      <div class="card-body p-4">
        <div class="text-center mb-3">
          <i class="bi bi-person-plus-fill fs-1 text-primary-tma"></i>
          <h4 class="mt-2 mb-0 fw-bold">Create User Account</h4>
          <p class="text-muted small">Register as a Trekker</p>
        </div>

        <div v-if="errorMsg" class="alert alert-danger py-2">{{ errorMsg }}</div>
        <div v-if="successMsg" class="alert alert-success py-2">{{ successMsg }}</div>

        <form @submit.prevent="handleRegister" v-if="!successMsg">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.name" type="text" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Contact Number</label>
            <input v-model="form.contact_number" type="tel" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required minlength="6" />
          </div>
          <div class="mb-3">
            <label class="form-label">Confirm Password</label>
            <input v-model="form.confirm_password" type="password" class="form-control" required minlength="6" />
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Register
          </button>
        </form>

        <div class="text-center mt-3">
          <small>Already have an account? <router-link to="/login">Login here</router-link></small>
        </div>

        <div class="alert alert-info small mt-3 mb-0">
          <i class="bi bi-info-circle me-1"></i>
          Only Users (Trekkers) can register themselves. Trekking Staff are created by Admin.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../store/auth'

const form = reactive({
  name: '', email: '', contact_number: '', password: '', confirm_password: '',
})
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const auth = useAuthStore()

async function handleRegister() {
  errorMsg.value = ''
  if (form.password !== form.confirm_password) {
    errorMsg.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.register(form)
    successMsg.value = 'Registration successful! You can now log in.'
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
