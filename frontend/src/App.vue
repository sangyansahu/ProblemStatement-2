<template>
  <div class="min-h-screen bg-canvas font-sans text-text-primary antialiased selection:bg-primary-soft selection:text-primary">
    <!-- Authenticated App Shell with Forest-Green Sidebar & Topbar -->
    <AppLayout v-if="!route.meta.public" />

    <!-- Public Landing & Login Pages -->
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import AppLayout from '@/components/layout/AppLayout.vue';

const route = useRoute();
</script>
