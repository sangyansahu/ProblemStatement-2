<template>
  <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-border">
    <div>
      <div class="flex items-center gap-2.5">
        <h1 class="text-[23px] sm:text-[25px] font-semibold text-text-primary tracking-tight font-sans leading-tight">
          {{ title }}
        </h1>
        <slot name="badge" />
      </div>
      <p v-if="description" class="text-[13px] text-text-secondary mt-1 max-w-2xl font-normal leading-relaxed">
        {{ description }}
      </p>
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2.5 shrink-0">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>
