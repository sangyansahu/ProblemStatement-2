<template>
  <div class="min-h-screen bg-canvas flex flex-col justify-center items-center p-4 antialiased">
    <!-- Login Card Container -->
    <div class="w-full max-w-[420px] bg-surface rounded-[8px] border border-border shadow-panel p-6 sm:p-8">
      <!-- Institutional Header -->
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-sm bg-[#2B665B] border border-[#3E7A6E] flex items-center justify-center shrink-0">
          <svg class="w-6 h-6 text-bronze" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <h2 class="text-[17px] font-semibold text-text-primary tracking-tight leading-tight">
            AICTE Portal Login
          </h2>
          <p class="text-[11px] text-text-secondary leading-tight mt-0.5">
            Student Data Management & Verification
          </p>
        </div>
      </div>

      <!-- Alert / Error message -->
      <div
        v-if="errorMessage"
        class="mb-4 p-3 rounded-[6px] bg-critical-bg border border-critical/30 text-critical text-[12px] flex items-start gap-2"
      >
        <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
        <span>{{ errorMessage }}</span>
      </div>

      <div
        v-if="isExpired"
        class="mb-4 p-3 rounded-[6px] bg-caution-bg border border-caution/30 text-caution text-[12px] flex items-start gap-2"
      >
        <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
        <span>Your session has expired. Please sign in again.</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="username">
            Account Identifier / Email
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            placeholder="e.g. institute_demo or your@institute.edu"
            class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-sans"
          />
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-[12px] font-medium text-text-secondary" for="password">
              Password
            </label>
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="text-[11px] text-primary hover:underline font-medium"
            >
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="Enter institutional password"
              class="w-full h-[40px] px-3 pr-10 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-sans"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
            >
              <Eye v-if="!showPassword" class="w-4 h-4" />
              <EyeOff v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full h-[42px] mt-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[13px] font-medium transition-colors shadow-subtle flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ authStore.isLoading ? 'Authenticating...' : 'Sign In to Portal' }}</span>
        </button>
      </form>

      <!-- Quick Demo Persona Fillers for Testing -->
      <div class="mt-6 pt-5 border-t border-border">
        <div class="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2.5 flex items-center justify-between">
          <span>Quick Evaluation Personas</span>
          <span class="text-[9px] font-mono text-primary font-normal">Click to fill</span>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <button
            type="button"
            @click="fillCredentials('institute_demo', 'Demo123!')"
            class="px-2 py-1.5 rounded-[4px] bg-canvas hover:bg-border text-text-secondary hover:text-text-primary border border-border text-[11px] font-medium text-center transition-colors truncate"
          >
            Institute
          </button>
          <button
            type="button"
            @click="fillCredentials('admin_demo', 'Demo123!')"
            class="px-2 py-1.5 rounded-[4px] bg-canvas hover:bg-border text-text-secondary hover:text-text-primary border border-border text-[11px] font-medium text-center transition-colors truncate"
          >
            Admin
          </button>
          <button
            type="button"
            @click="fillCredentials('superadmin_demo', 'Demo123!')"
            class="px-2 py-1.5 rounded-[4px] bg-canvas hover:bg-border text-text-secondary hover:text-text-primary border border-border text-[11px] font-medium text-center transition-colors truncate"
          >
            Super Admin
          </button>
        </div>
      </div>

      <!-- Back to Landing -->
      <div class="mt-5 text-center">
        <router-link to="/" class="text-[12px] text-text-secondary hover:text-primary transition-colors">
          ← Return to Portal Overview
        </router-link>
      </div>
    </div>

    <!-- Security Note -->
    <div class="mt-6 text-center text-[11px] text-text-secondary max-w-sm">
      This is a secure Government of India educational data management portal. Unauthorized access attempts are monitored and recorded.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const username = ref('institute_demo');
const password = ref('Demo123!');
const showPassword = ref(false);
const errorMessage = ref('');
const isExpired = ref(route.query.expired === '1');

function fillCredentials(u: string, p: string) {
  username.value = u;
  password.value = p;
  errorMessage.value = '';
}

async function handleSubmit() {
  errorMessage.value = '';
  isExpired.value = false;

  const res = await authStore.login(username.value.trim(), password.value);
  if (res.success) {
    router.push('/dashboard');
  } else {
    errorMessage.value = res.message || 'Invalid username or password';
  }
}
</script>
