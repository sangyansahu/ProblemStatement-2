<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <PageHeader
        title="Notifications Center"
        description="Operational alerts, validation issues, duplicate conflict warnings, and system notices."
      />
      <div class="flex items-center gap-3">
        <button
          v-if="notifStore.unreadCount > 0"
          type="button"
          @click="notifStore.markAllAsRead"
          class="px-3.5 py-2 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px] font-medium text-text-primary transition-colors flex items-center gap-1.5 shadow-subtle"
        >
          <CheckCheck class="w-4 h-4 text-primary" />
          <span>Mark All as Read</span>
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex items-center gap-2 border-b border-border pb-2 text-[13px]">
      <button
        type="button"
        @click="filterType = 'all'"
        :class="[
          'px-3 py-1.5 rounded-[4px] font-medium transition-colors',
          filterType === 'all' ? 'bg-surface border border-border text-primary shadow-subtle' : 'text-text-secondary hover:text-text-primary'
        ]"
      >
        All ({{ notifStore.notifications.length }})
      </button>
      <button
        type="button"
        @click="filterType = 'unread'"
        :class="[
          'px-3 py-1.5 rounded-[4px] font-medium transition-colors flex items-center gap-1.5',
          filterType === 'unread' ? 'bg-surface border border-border text-primary shadow-subtle' : 'text-text-secondary hover:text-text-primary'
        ]"
      >
        <span>Unread</span>
        <span v-if="notifStore.unreadCount > 0" class="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-critical text-surface font-semibold">
          {{ notifStore.unreadCount }}
        </span>
      </button>
      <button
        type="button"
        @click="filterType = 'critical'"
        :class="[
          'px-3 py-1.5 rounded-[4px] font-medium transition-colors',
          filterType === 'critical' ? 'bg-surface border border-border text-critical shadow-subtle' : 'text-text-secondary hover:text-text-primary'
        ]"
      >
        Critical / Warnings
      </button>
    </div>

    <!-- Notification List -->
    <div class="bg-surface border border-border rounded-[8px] divide-y divide-border/60 shadow-subtle overflow-hidden">
      <div v-if="filteredNotifications.length === 0" class="p-12 text-center text-text-secondary">
        <BellOff class="w-8 h-8 text-text-secondary/40 mx-auto mb-2" />
        <p class="text-[13px] font-medium">No notifications in this category</p>
        <p class="text-[11px] text-text-secondary mt-1">Operational alerts and batch import updates will appear here.</p>
      </div>

      <div
        v-for="notif in filteredNotifications"
        :key="notif.id"
        :class="[
          'p-4 sm:p-5 flex items-start gap-4 transition-colors',
          !notif.is_read ? 'bg-primary-soft/15 font-medium' : 'hover:bg-canvas/50'
        ]"
      >
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5',
            notif.type === 'critical' ? 'bg-critical-bg text-critical' : notif.type === 'warning' ? 'bg-caution-bg text-caution' : 'bg-primary-soft text-primary'
          ]"
        >
          <AlertCircle v-if="notif.type === 'critical'" class="w-4 h-4" />
          <AlertTriangle v-else-if="notif.type === 'warning'" class="w-4 h-4" />
          <Info v-else class="w-4 h-4" />
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-baseline justify-between gap-2">
            <h4 class="text-[14px] font-semibold text-text-primary leading-tight">
              {{ notif.title }}
            </h4>
            <span class="text-[11px] font-mono text-text-secondary shrink-0">
              {{ formatDate(notif.created_at) }}
            </span>
          </div>

          <p class="text-[13px] text-text-secondary mt-1 leading-relaxed font-normal">
            {{ notif.message }}
          </p>

          <div class="mt-3 flex items-center gap-3 text-[12px]">
            <router-link
              v-if="notif.link"
              :to="notif.link"
              class="text-primary hover:underline font-medium inline-flex items-center gap-1"
            >
              <span>View Related Record</span>
              <ArrowRight class="w-3.5 h-3.5" />
            </router-link>
            <button
              v-if="!notif.is_read"
              type="button"
              @click="notifStore.markAsRead(notif.id)"
              class="text-text-secondary hover:text-text-primary hover:underline"
            >
              Mark as read
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useNotificationStore } from '@/stores/notification';
import PageHeader from '@/components/common/PageHeader.vue';
import {
  BellOff,
  CheckCheck,
  AlertCircle,
  AlertTriangle,
  Info,
  ArrowRight
} from 'lucide-vue-next';

const notifStore = useNotificationStore();
const filterType = ref<'all' | 'unread' | 'critical'>('all');

const filteredNotifications = computed(() => {
  if (filterType.value === 'unread') {
    return notifStore.notifications.filter((n) => !n.is_read);
  }
  if (filterType.value === 'critical') {
    return notifStore.notifications.filter((n) => n.type === 'critical' || n.type === 'warning');
  }
  return notifStore.notifications;
});

function formatDate(iso: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>
