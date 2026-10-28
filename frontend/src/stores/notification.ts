import { defineStore } from 'pinia';
import { ref } from 'vue';
import { notificationsApi } from '@/services/api';
import type { Notification } from '@/types';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([]);
  const unreadCount = ref(0);
  const isLoading = ref(false);

  async function fetchNotifications() {
    isLoading.value = true;
    try {
      const res = await notificationsApi.list();
      notifications.value = res.data.notifications;
      unreadCount.value = res.data.unread_count;
    } catch (err) {
      // Non-intrusive
    } finally {
      isLoading.value = false;
    }
  }

  async function markAsRead(id: number) {
    try {
      await notificationsApi.markAsRead(id);
      const notif = notifications.value.find((n) => n.id === id);
      if (notif && !notif.is_read) {
        notif.is_read = true;
        unreadCount.value = Math.max(0, unreadCount.value - 1);
      }
    } catch (err) {}
  }

  async function markAllAsRead() {
    try {
      await notificationsApi.markAllAsRead();
      notifications.value.forEach((n) => (n.is_read = true));
      unreadCount.value = 0;
    } catch (err) {}
  }

  return {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  };
});
