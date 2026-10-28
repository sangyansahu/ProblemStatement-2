<template>
  <div class="space-y-6">
    <InstituteDashboardView v-if="authStore.isInstitute" />
    <AdminDashboardView v-else-if="authStore.isAdmin" />
    <SuperAdminDashboardView v-else-if="authStore.isSuperAdmin" />
    <div v-else class="p-8 text-center bg-surface border border-border rounded-[8px]">
      <p class="text-text-secondary text-sm">Determining authorized portal view...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import InstituteDashboardView from './InstituteDashboardView.vue';
import AdminDashboardView from './AdminDashboardView.vue';
import SuperAdminDashboardView from './SuperAdminDashboardView.vue';

const authStore = useAuthStore();
</script>
