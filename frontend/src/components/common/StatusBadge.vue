<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm text-[11px] font-medium border font-mono select-none',
      config.bgClass,
      config.textClass,
      config.borderClass
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full shrink-0', config.dotClass]"></span>
    <span>{{ config.label }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status: string;
}>();

const config = computed(() => {
  const s = (props.status || '').toLowerCase().replace(/[\s-]/g, '_');

  switch (s) {
    case 'verified':
      return {
        label: 'Verified',
        dotClass: 'bg-success',
        bgClass: 'bg-success-bg',
        textClass: 'text-success',
        borderClass: 'border-success/30',
      };
    case 'pending':
    case 'in_progress':
    case 'processing':
      return {
        label: 'Pending',
        dotClass: 'bg-caution',
        bgClass: 'bg-caution-bg',
        textClass: 'text-caution',
        borderClass: 'border-caution/30',
      };
    case 'requires_manual_review':
    case 'in_review':
      return {
        label: 'In Review',
        dotClass: 'bg-bronze',
        bgClass: 'bg-[#F9F4EC]',
        textClass: 'text-[#966735]',
        borderClass: 'border-bronze/30',
      };
    case 'mismatch_detected':
    case 'mismatch':
      return {
        label: 'Mismatch',
        dotClass: 'bg-critical',
        bgClass: 'bg-critical-bg',
        textClass: 'text-critical',
        borderClass: 'border-critical/30',
      };
    case 'unable_to_verify':
      return {
        label: 'Unable to Verify',
        dotClass: 'bg-caution',
        bgClass: 'bg-caution-bg',
        textClass: 'text-caution',
        borderClass: 'border-caution/30',
      };
    case 'rejected':
    case 'failed':
    case 'critical':
      return {
        label: 'Rejected',
        dotClass: 'bg-critical',
        bgClass: 'bg-critical-bg',
        textClass: 'text-critical',
        borderClass: 'border-critical/30',
      };
    case 'not_submitted':
      return {
        label: 'Not Submitted',
        dotClass: 'bg-[#7E8B87]',
        bgClass: 'bg-[#EDEDEA]',
        textClass: 'text-[#475551]',
        borderClass: 'border-border',
      };
    case 'active':
    case 'completed':
    case 'resolved':
      return {
        label: s.charAt(0).toUpperCase() + s.slice(1),
        dotClass: 'bg-success',
        bgClass: 'bg-success-bg',
        textClass: 'text-success',
        borderClass: 'border-success/30',
      };
    case 'open':
      return {
        label: 'Open Conflict',
        dotClass: 'bg-caution',
        bgClass: 'bg-caution-bg',
        textClass: 'text-caution',
        borderClass: 'border-caution/30',
      };
    default:
      return {
        label: props.status || 'Unknown',
        dotClass: 'bg-text-secondary',
        bgClass: 'bg-canvas',
        textClass: 'text-text-secondary',
        borderClass: 'border-border',
      };
  }
});
</script>
