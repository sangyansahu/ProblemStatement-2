<template>
  <div class="bg-surface rounded-[8px] border border-border p-4.5 shadow-subtle flex flex-col justify-between transition-colors hover:border-border-strong">
    <div class="flex items-center justify-between gap-2">
      <span class="text-[12px] font-medium text-text-secondary uppercase tracking-wider">{{ label }}</span>
      <div v-if="icon" class="p-1.5 rounded-md bg-canvas text-text-secondary">
        <component :is="icon" class="w-4 h-4" />
      </div>
    </div>
    <div class="mt-2.5 flex items-baseline justify-between gap-2">
      <div class="text-[26px] font-semibold text-text-primary tracking-tight font-sans">
        {{ value }}
      </div>
      <div v-if="changeText" :class="['text-[11px] font-medium px-1.5 py-0.5 rounded-sm', changeClass]">
        {{ changeText }}
      </div>
    </div>
    <div v-if="subtext" class="mt-2 text-[11px] text-text-secondary truncate">
      {{ subtext }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  label: string;
  value: string | number;
  subtext?: string;
  changeText?: string;
  changeType?: 'positive' | 'negative' | 'neutral' | 'caution';
  icon?: any;
}>();

const changeClass = computed(() => {
  if (props.changeType === 'positive') return 'bg-success-bg text-success border border-success/20';
  if (props.changeType === 'negative') return 'bg-critical-bg text-critical border border-critical/20';
  if (props.changeType === 'caution') return 'bg-caution-bg text-caution border border-caution/20';
  return 'bg-canvas text-text-secondary border border-border';
});
</script>
