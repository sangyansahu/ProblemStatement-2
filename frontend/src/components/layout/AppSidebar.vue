<template>
  <div>
    <!-- Mobile Drawer Overlay -->
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-40 bg-black/50 backdrop-blur-xs md:hidden"
      @click="$emit('close-mobile')"
    ></div>

    <!-- Sidebar Container -->
    <aside
      :class="[
        'fixed top-0 bottom-0 left-0 z-50 flex flex-col w-[248px] bg-sidebar transition-transform duration-200 ease-in-out select-none border-r border-[#2C4541]',
        mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      ]"
    >
      <!-- Top Institutional Identity -->
      <div class="pt-[25px] px-[15px] pb-5 border-b border-[#2C4541]">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-sm bg-[#2B665B] border border-[#3E7A6E] flex items-center justify-center shrink-0 shadow-xs">
            <svg class="w-5 h-5 text-bronze" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <div class="font-bold text-[15px] tracking-wide text-[#FFFEFA] leading-tight flex items-center gap-1.5">
              <span>AICTE</span>
              <span class="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded-xs bg-[#2B665B]/70 text-[#E1EEEA] font-mono font-medium">
                {{ roleLabel }}
              </span>
            </div>
            <div class="text-[11px] text-[#A9B8B1] leading-tight mt-0.5 font-normal">
              Student Data Management<br />& Verification Portal
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-1 overflow-y-auto px-[15px] py-4 space-y-1">
        <template v-for="item in navItems" :key="item.path">
          <router-link
            :to="item.path"
            @click="$emit('close-mobile')"
            :class="[
              'group flex items-center h-[43px] px-3 rounded-[6px] text-[13px] font-medium transition-colors relative',
              isActive(item.path)
                ? 'bg-[rgba(237,244,236,0.105)] text-[#FFFEFA]'
                : 'text-[#A9B8B1] hover:text-[#FFFEFA] hover:bg-[rgba(255,255,255,0.055)]'
            ]"
          >
            <!-- Bronze Active Left-Edge Indicator (Exact: 3px solid #D8A36C) -->
            <span
              v-if="isActive(item.path)"
              class="absolute left-0 top-[6px] bottom-[6px] w-[3px] bg-bronze rounded-r"
            ></span>

            <!-- Icon -->
            <component
              :is="item.icon"
              :class="[
                'w-[18px] h-[18px] shrink-0 mr-3 transition-colors',
                isActive(item.path) ? 'text-[#FFFEFA]' : 'text-[#A9B8B1] group-hover:text-[#FFFEFA]'
              ]"
            />

            <!-- Label -->
            <span class="truncate">{{ item.label }}</span>

            <!-- Badges if applicable -->
            <span
              v-if="item.badge"
              class="ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-bronze/20 text-bronze border border-bronze/30 font-semibold"
            >
              {{ item.badge }}
            </span>
          </router-link>
        </template>
      </nav>

      <!-- Bottom User Context & Portal Version -->
      <div class="p-3.5 border-t border-[#2C4541] bg-[#1B2D2A]">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-full bg-[#2B665B] text-surface flex items-center justify-center font-semibold text-[11px] shrink-0">
            {{ userInitials }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-[12px] font-medium text-[#FFFEFA] truncate leading-tight">
              {{ authStore.user?.full_name || 'Authorized User' }}
            </div>
            <div class="text-[10px] text-[#A9B8B1] truncate font-mono mt-0.5">
              {{ authStore.user?.institution_code || authStore.role?.toUpperCase() }}
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import {
  LayoutDashboard,
  Building2,
  Users,
  UploadCloud,
  History,
  ShieldCheck,
  Copy,
  BarChart3,
  Bell,
  Sliders,
  Settings,
  Scale,
  FileText
} from 'lucide-vue-next';

interface NavItem {
  label: string;
  path: string;
  icon: any;
  badge?: string | number;
}

defineProps<{
  mobileOpen: boolean;
}>();

defineEmits<{
  (e: 'close-mobile'): void;
}>();

const route = useRoute();
const authStore = useAuthStore();

const roleLabel = computed(() => {
  if (authStore.isInstitute) return 'Institute';
  if (authStore.isAdmin) return 'Admin';
  if (authStore.isSuperAdmin) return 'Super Admin';
  return 'Guest';
});

const userInitials = computed(() => {
  const name = authStore.user?.full_name || 'U';
  return name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();
});

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
}

// Role-based navigation specification strictly followed
const navItems = computed<NavItem[]>(() => {
  const role = authStore.role;

  if (role === 'institute') {
    return [
      { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
      { label: 'My Institution', path: '/my-institution', icon: Building2 },
      { label: 'Student Directory', path: '/students', icon: Users },
      { label: 'Bulk CSV Upload', path: '/bulk-upload', icon: UploadCloud },
      { label: 'Verification Status', path: '/verification', icon: ShieldCheck },
      { label: 'Duplicate Review', path: '/duplicate-review', icon: Copy },
      { label: 'Reports', path: '/reports', icon: BarChart3 },
      { label: 'Notifications', path: '/notifications', icon: Bell },
      { label: 'Profile and Settings', path: '/settings', icon: Settings },
    ];
  }

  if (role === 'admin') {
    return [
      { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
      { label: 'Verification Queue', path: '/verification', icon: ShieldCheck },
      { label: 'Duplicate Review', path: '/duplicate-review', icon: Copy },
      { label: 'Enrolment Monitoring', path: '/enrolment-monitoring', icon: Scale },
      { label: 'Reports and Analytics', path: '/reports', icon: BarChart3 },
      { label: 'Audit Logs', path: '/audit-logs', icon: FileText },
      { label: 'Notifications', path: '/notifications', icon: Bell },
      { label: 'Profile & Settings', path: '/settings', icon: Settings },
    ];
  }

  // Super Admin
  return [
    { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Institution Management', path: '/institutions', icon: Building2 },
    { label: 'Verification Management', path: '/verification', icon: ShieldCheck },
    { label: 'Duplicate & Conflict Review', path: '/duplicate-review', icon: Copy },
    { label: 'Enrolment and Intake', path: '/enrolment-monitoring', icon: Scale },
    { label: 'Reports and Analytics', path: '/reports', icon: BarChart3 },
    { label: 'User Management', path: '/users', icon: Users },
    { label: 'Audit Logs', path: '/audit-logs', icon: FileText },
    { label: 'System Settings', path: '/settings', icon: Sliders },
  ];
});
</script>
