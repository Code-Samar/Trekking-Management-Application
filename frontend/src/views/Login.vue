<template>
  <div class="login-page">
    <section class="login-visual">
      <div class="login-copy">
        <div class="d-flex align-items-center gap-2 mb-5"><span class="brand-mark bg-white text-primary-tma"><i class="bi bi-signpost-split-fill"></i></span><strong class="fs-5">TrekFlow</strong></div>
        <div class="page-kicker text-white-50">Trekking Management Platform</div>
        <h1 class="mt-2 mb-4">Plan the trail.<br><span style="color:#a9e3cb">Own the journey.</span></h1>
        <p>One beautiful workspace for discovering treks, managing bookings, coordinating staff and keeping every adventure on track.</p>
      </div>
      <div class="d-flex flex-wrap gap-4">
        <div class="login-feature"><i class="bi bi-check-circle-fill"></i> Simple booking</div>
        <div class="login-feature"><i class="bi bi-check-circle-fill"></i> Live trek management</div>
        <div class="login-feature"><i class="bi bi-check-circle-fill"></i> Centralized reports</div>
      </div>
    </section>

    <section class="login-panel">
      <div class="login-card">
        <div class="login-logo mb-4"><i class="bi bi-signpost-split-fill"></i></div>
        <h3 class="fw-bold mb-1">Welcome back</h3>
        <p class="text-muted mb-4">Sign in to continue your journey.</p>

        <div class="role-tabs nav nav-pills nav-fill mb-4">
          <a v-for="r in roles" :key="r.value" class="nav-link" :class="{active: role === r.value}" href="#" @click.prevent="role = r.value">
            <i :class="r.icon" class="me-1"></i>{{ r.label }}
          </a>
        </div>

        <div v-if="errorMsg" class="alert alert-danger py-2 small border-0 rounded-3">{{ errorMsg }}</div>
        <form @submit.prevent="handleLogin">
          <div class="mb-3"><label class="form-label">Email address</label><input v-model="email" type="email" class="form-control" placeholder="you@example.com" required /></div>
          <div class="mb-4"><div class="d-flex justify-content-between"><label class="form-label">Password</label></div><input v-model="password" type="password" class="form-control" placeholder="Enter your password" required minlength="6" /></div>
          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading"><span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>{{ loading ? 'Signing in…' : 'Sign in' }} <i v-if="!loading" class="bi bi-arrow-right ms-1"></i></button>
        </form>
        <div class="text-center mt-4" v-if="role === 'trekker'"><small class="text-muted">New to TrekFlow? <router-link to="/register" class="fw-bold">Create an account</router-link></small></div>
        <div class="alert alert-info small mt-4 mb-0 border-0 rounded-3"><i class="bi bi-info-circle me-1"></i> Users can register themselves. Staff accounts are created by Admin.</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
const email = ref(''); const password = ref(''); const role = ref('trekker'); const loading = ref(false); const errorMsg = ref('')
const roles = [{ value:'admin',label:'Admin',icon:'bi bi-shield-lock' },{ value:'staff',label:'Staff',icon:'bi bi-person-badge' },{ value:'trekker',label:'User',icon:'bi bi-person' }]
const auth = useAuthStore(); const router = useRouter()
async function handleLogin(){ errorMsg.value=''; loading.value=true; try { const user=await auth.login(email.value,password.value,role.value); const dest=user.role==='trekker'?'user-dashboard':`${user.role}-dashboard`; router.push({name:dest}) } catch(err){ errorMsg.value=err.response?.data?.error||'Login failed. Please try again.' } finally { loading.value=false } }
</script>
