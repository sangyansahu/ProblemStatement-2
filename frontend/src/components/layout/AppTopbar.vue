<template>
  <header class="sticky top-0 z-30 min-h-[69px] bg-surface border-b border-border px-4 lg:px-[36px] flex items-center justify-between gap-4">
    <!-- Left: Mobile Menu Toggle & Breadcrumbs -->
    <div class="flex items-center gap-3">
      <button
        type="button"
        @click="$emit('toggle-mobile')"
        class="md:hidden p-2 rounded-md text-text-secondary hover:bg-canvas hover:text-text-primary focus:outline-none"
        aria-label="Toggle navigation menu"
      >
        <Menu class="w-5 h-5" />
      </button>

      <div class="hidden sm:flex items-center gap-2 text-[13px] text-text-secondary">
        <span class="font-medium text-text-primary">AICTE Portal</span>
        <ChevronRight class="w-3.5 h-3.5 text-text-secondary/60" />
        <span class="font-normal capitalize">{{ currentRouteTitle }}</span>
      </div>
    </div>

    <!-- Center: Global Search -->
    <div class="flex-1 max-w-md mx-2">
      <div class="relative">
        <Search class="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="Search by Student ID, APAAR, or Institution..."
          class="w-full h-[38px] pl-9 pr-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary placeholder:text-text-secondary/70 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-sans"
        />
      </div>
    </div>

    <!-- Right Controls: Role Badge, Quick Demo Switcher, Notifications, User Dropdown -->
    <div class="flex items-center gap-3">
      <!-- Quick Demo Role Switcher -->
      <div class="relative">
        <button
          type="button"
          @click="roleDropdownOpen = !roleDropdownOpen"
          class="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-[6px] bg-primary-soft/80 hover:bg-primary-soft text-primary border border-primary/20 text-[11px] font-semibold tracking-wide transition-colors"
          title="Switch persona for testing different roles"
        >
          <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span>ROLE: {{ activeRoleTitle }}</span>
          <ChevronDown class="w-3.5 h-3.5 text-primary" />
        </button>

        <div
          v-if="roleDropdownOpen"
          class="absolute right-0 mt-2 w-52 bg-surface border border-border rounded-[8px] shadow-panel py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100"
        >
          <div class="px-3 py-1.5 text-[11px] font-semibold text-text-secondary border-b border-border/60 uppercase tracking-wider">
            Switch Demo Persona
          </div>
          <button
            type="button"
            @click="switchRole('institute')"
            class="w-full text-left px-3 py-2 text-[12px] flex items-center justify-between hover:bg-canvas transition-colors"
            :class="authStore.isInstitute ? 'font-semibold text-primary bg-primary-soft/40' : 'text-text-primary'"
          >
            <span>Institute (DIAET Delhi)</span>
            <span v-if="authStore.isInstitute" class="text-xs text-primary">✓</span>
          </button>
          <button
            type="button"
            @click="switchRole('admin')"
            class="w-full text-left px-3 py-2 text-[12px] flex items-center justify-between hover:bg-canvas transition-colors"
            :class="authStore.isAdmin ? 'font-semibold text-primary bg-primary-soft/40' : 'text-text-primary'"
          >
            <span>Admin (Regional Officer)</span>
            <span v-if="authStore.isAdmin" class="text-xs text-primary">✓</span>
          </button>
          <button
            type="button"
            @click="switchRole('super_admin')"
            class="w-full text-left px-3 py-2 text-[12px] flex items-center justify-between hover:bg-canvas transition-colors"
            :class="authStore.isSuperAdmin ? 'font-semibold text-primary bg-primary-soft/40' : 'text-text-primary'"
          >
            <span>Super Admin (AICTE HQ)</span>
            <span v-if="authStore.isSuperAdmin" class="text-xs text-primary">✓</span>
          </button>
        </div>
      </div>

      <!-- Notifications Bell -->
      <div class="relative">
        <button
          type="button"
          @click="notifDrawerOpen = !notifDrawerOpen"
          class="relative p-2 rounded-[6px] text-text-secondary hover:text-text-primary hover:bg-canvas border border-transparent hover:border-border transition-colors"
          aria-label="View notifications"
        >
          <Bell class="w-4 h-4" />
          <span
            v-if="notifStore.unreadCount > 0"
            class="absolute top-1 right-1 w-2 h-2 rounded-full bg-critical border border-surface"
          ></span>
        </button>

        <!-- Notifications Dropdown -->
        <div
          v-if="notifDrawerOpen"
          class="absolute right-0 mt-2 w-80 sm:w-96 bg-surface border border-border rounded-[8px] shadow-panel py-2 z-50"
        >
          <div class="px-3.5 py-2 border-b border-border flex items-center justify-between">
            <span class="text-[13px] font-semibold text-text-primary">Notifications</span>
            <button
              v-if="notifStore.unreadCount > 0"
              @click="notifStore.markAllAsRead"
              class="text-[11px] text-primary hover:underline font-medium"
            >
              Mark all as read
            </button>
          </div>
          <div class="max-h-72 overflow-y-auto divide-y divide-border/60">
            <template v-if="notifStore.notifications.length === 0">
              <div class="p-4 text-center text-text-secondary text-[12px]">
                No new notifications
              </div>
            </template>
            <div
              v-for="notif in notifStore.notifications"
              :key="notif.id"
              @click="markRead(notif.id)"
              :class="[
                'p-3 cursor-pointer hover:bg-canvas transition-colors text-[12px]',
                !notif.is_read ? 'bg-primary-soft/20 font-medium' : ''
              ]"
            >
              <div class="flex items-start justify-between gap-2">
                <span class="text-text-primary leading-tight">{{ notif.title }}</span>
                <span
                  :class="[
                    'w-2 h-2 rounded-full shrink-0 mt-1',
                    notif.type === 'critical' ? 'bg-critical' : notif.type === 'warning' ? 'bg-caution' : 'bg-primary'
                  ]"
                ></span>
              </div>
              <p class="text-[11px] text-text-secondary mt-1 leading-normal font-normal">
                {{ notif.message }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- User Account Dropdown -->
      <div class="relative">
        <button
          type="button"
          @click="userMenuOpen = !userMenuOpen"
          class="flex items-center gap-2 p-1.5 rounded-[6px] hover:bg-canvas border border-transparent hover:border-border transition-colors text-left"
        >
          <div class="w-8 h-8 rounded-full bg-primary text-surface flex items-center justify-center font-medium text-[12px]">
            {{ initials }}
          </div>
          <div class="hidden lg:block">
            <div class="text-[12px] font-semibold text-text-primary leading-tight">
              {{ authStore.user?.full_name || 'User' }}
            </div>
            <div class="text-[10px] text-text-secondary font-mono mt-0.5">
              {{ authStore.user?.role?.toUpperCase() }}
            </div>
          </div>
          <ChevronDown class="w-3.5 h-3.5 text-text-secondary hidden lg:block" />
        </button>

        <div
          v-if="userMenuOpen"
          class="absolute right-0 mt-2 w-56 bg-surface border border-border rounded-[8px] shadow-panel py-1.5 z-50"
        >
          <div class="px-3.5 py-2 border-b border-border/80">
            <div class="text-[12px] font-semibold text-text-primary">{{ authStore.user?.full_name }}</div>
            <div class="text-[11px] text-text-secondary font-mono truncate">{{ authStore.user?.email }}</div>
          </div>
          <router-link
            to="/settings"
            @click="userMenuOpen = false"
            class="flex items-center gap-2 px-3.5 py-2 text-[12px] text-text-primary hover:bg-canvas transition-colors"
          >
            <Settings class="w-4 h-4 text-text-secondary" />
            <span>Profile & Settings</span>
          </router-link>
          <button
            type="button"
            @click="handleSignOut"
            class="w-full text-left flex items-center gap-2 px-3.5 py-2 text-[12px] text-critical hover:bg-critical-bg transition-colors"
          >
            <LogOut class="w-4 h-4 text-critical" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import {
  Menu,
  Search,
  Bell,
  ChevronDown,
  ChevronRight,
  Settings,
  LogOut
} from 'lucide-vue-next';

defineEmits<{
  (e: 'toggle-mobile'): void;
}>();

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notifStore = useNotificationStore();

const searchQuery = ref('');
const roleDropdownOpen = ref(false);
const notifDrawerOpen = ref(false);
const userMenuOpen = ref(false);

const currentRouteTitle = computed(() => {
  return String(route.name || route.path.replace('/', '') || 'Overview');
});

const activeRoleTitle = computed(() => {
  if (authStore.isInstitute) return 'INSTITUTE';
  if (authStore.isAdmin) return 'ADMIN';
  if (authStore.isSuperAdmin) return 'SUPER ADMIN';
  return 'GUEST';
});

const initials = computed(() => {
  const name = authStore.user?.full_name || 'U';
  return name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();
});

function handleSearch() {
  if (!searchQuery.value.trim()) return;
  router.push({ path: '/students', query: { search: searchQuery.value.trim() } });
}

async function switchRole(role: 'institute' | 'admin' | 'super_admin') {
  roleDropdownOpen.value = false;
  await authStore.switchDemoRole(role);
  // Reload current route or push to dashboard
  router.push('/dashboard').then(() => {
    window.location.reload();
  });
}

function markRead(id: number) {
  notifStore.markAsRead(id);
}

function handleSignOut() {
  userMenuOpen.value = false;
  authStore.logout();
  router.push('/login');
}

// Click outside to close menus
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  if (!target.closest('.relative')) {
    roleDropdownOpen.value = false;
    notifDrawerOpen.value = false;
    userMenuOpen.value = false;
  }
}

onMounted(() => {
  notifStore.fetchNotifications();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
