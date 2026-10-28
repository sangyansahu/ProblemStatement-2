<template>
  <div class="min-h-screen bg-canvas flex flex-col antialiased">
    <!-- Fixed Desktop / Drawer Mobile Sidebar -->
    <AppSidebar
      :mobile-open="mobileSidebarOpen"
      @close-mobile="mobileSidebarOpen = false"
    />

    <!-- Main Content Shell (Pushed by 248px desktop sidebar) -->
    <div class="flex-1 md:pl-[248px] flex flex-col min-w-0 transition-all duration-200">
      <!-- Sticky Topbar -->
      <AppTopbar @toggle-mobile="mobileSidebarOpen = !mobileSidebarOpen" />

      <!-- Main Canvas Area -->
      <main class="flex-1 p-4 sm:p-6 lg:p-[32px] max-w-7xl w-full mx-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade-fast" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- Institutional Footer -->
      <footer class="border-t border-border bg-surface/50 py-3 px-6 text-center text-[11px] text-text-secondary flex flex-col sm:flex-row items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="font-semibold text-text-primary">AICTE</span>
          <span>•</span>
          <span>All India Council for Technical Education, Government of India</span>
        </div>
        <div class="flex items-center gap-3 font-mono text-[10px]">
          <span>PORTAL v1.0.0</span>
          <span>•</span>
          <span class="text-primary font-medium">APAAR REGISTRY ACTIVE</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppSidebar from './AppSidebar.vue';
import AppTopbar from './AppTopbar.vue';

const mobileSidebarOpen = ref(false);
</script>

<style scoped>
.fade-fast-enter-active,
.fade-fast-leave-active {
  transition: opacity 0.12s ease;
}
.fade-fast-enter-from,
.fade-fast-leave-to {
  opacity: 0;
}
</style>
