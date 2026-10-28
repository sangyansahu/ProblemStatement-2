<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity" @click="$emit('close')"></div>

        <!-- Modal Content Container -->
        <div
          :class="[
            'relative bg-surface rounded-[8px] border border-border shadow-panel w-full overflow-hidden z-10 flex flex-col my-8 max-h-[90vh]',
            maxWidthClass
          ]"
        >
          <!-- Header -->
          <div class="px-5 py-4 border-b border-border flex items-center justify-between bg-surface">
            <h3 class="text-[16px] font-semibold text-text-primary tracking-tight">
              {{ title }}
            </h3>
            <button
              type="button"
              @click="$emit('close')"
              class="p-1 rounded-sm text-text-secondary hover:text-text-primary hover:bg-canvas transition-colors"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Body -->
          <div class="p-5 overflow-y-auto flex-1 font-sans text-[13px] text-text-primary">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="px-5 py-3.5 border-t border-border bg-canvas/40 flex items-center justify-end gap-2.5">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { X } from 'lucide-vue-next';

const props = withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl';
  }>(),
  {
    maxWidth: 'md',
  }
);

defineEmits<{
  (e: 'close'): void;
}>();

const maxWidthClass = computed(() => {
  switch (props.maxWidth) {
    case 'sm': return 'max-w-sm';
    case 'md': return 'max-w-md';
    case 'lg': return 'max-w-lg';
    case 'xl': return 'max-w-xl';
    case '2xl': return 'max-w-2xl';
    case '4xl': return 'max-w-4xl';
    default: return 'max-w-md';
  }
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
