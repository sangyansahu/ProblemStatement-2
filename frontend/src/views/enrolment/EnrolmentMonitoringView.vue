<template>
  <div class="space-y-6">
    <PageHeader
      title="Enrolment & Approved-Intake Monitoring"
      description="Programme-wise intake capacity monitoring, supernumerary allowance accounting, and enrolment utilization reconciliation."
    >
      <template #badge>
        <span class="px-2 py-0.5 rounded-sm bg-primary-soft text-primary font-mono text-[11px] font-semibold border border-primary/20">
          RECONCILIATION ENGINE
        </span>
      </template>
    </PageHeader>

    <!-- Synthetic Data Notice (Section 17 Requirement) -->
    <div class="bg-primary-soft/30 border border-primary/30 rounded-[8px] p-3.5 text-[12px] flex items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-primary shrink-0"></span>
        <span class="text-text-primary">
          Intake figures displayed below incorporate authoritative approval data or clearly labelled synthetic demonstration values.
        </span>
      </div>
      <span class="font-mono text-[11px] text-primary shrink-0 font-medium">DEMO DATASET ACTIVE</span>
    </div>

    <!-- Summary Metrics -->
    <div v-if="summary" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Programmes Tracked</span>
        <span class="text-[24px] font-semibold text-text-primary font-mono block mt-1">{{ summary.total_programmes || 0 }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Total Approved Intake</span>
        <span class="text-[24px] font-semibold text-text-primary font-mono block mt-1">{{ summary.total_approved_intake || 0 }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Actual Enrolment</span>
        <span class="text-[24px] font-semibold text-text-primary font-mono block mt-1">{{ summary.total_enrolled || 0 }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Capacity Utilization</span>
        <span class="text-[24px] font-semibold text-primary font-mono block mt-1">{{ summary.overall_utilization_rate || 0 }}%</span>
      </div>
    </div>

    <!-- Programme Enrolment Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Code</th>
              <th class="py-2.5 px-4">Programme & Branch</th>
              <th class="py-2.5 px-4">Institution</th>
              <th class="py-2.5 px-4">Year</th>
              <th class="py-2.5 px-4 font-mono">Approved</th>
              <th class="py-2.5 px-4 font-mono">Supernumerary</th>
              <th class="py-2.5 px-4 font-mono">Enrolled</th>
              <th class="py-2.5 px-4">Utilization</th>
              <th class="py-2.5 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="9" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading enrolment monitoring records...</span>
              </td>
            </tr>
            <tr v-for="p in programmes" :key="p.id" class="hover:bg-canvas/50 transition-colors">
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ p.programme_code }}</td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary">{{ p.programme_name }}</div>
                <div class="text-[11px] text-text-secondary">{{ p.branch_or_department }}</div>
              </td>
              <td class="py-3 px-4 text-text-secondary truncate max-w-[150px]">
                {{ p.institution_name }}
              </td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">{{ p.academic_year }}</td>
              <td class="py-3 px-4 font-mono text-text-primary">{{ p.approved_intake }}</td>
              <td class="py-3 px-4 font-mono text-text-secondary">+{{ p.supernumerary_intake }}</td>
              <td class="py-3 px-4 font-mono font-semibold text-text-primary">{{ p.actual_enrolment }}</td>
              <td class="py-3 px-4 font-mono">
                <div class="flex items-center gap-2">
                  <span>{{ p.utilization_rate }}%</span>
                  <div class="w-16 h-1.5 bg-canvas rounded-full overflow-hidden">
                    <div
                      class="h-full bg-progress rounded-full"
                      :style="{ width: `${Math.min(100, p.utilization_rate)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-right">
                <StatusBadge :status="p.discrepancy_status" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { enrolmentsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import { Loader2 } from 'lucide-vue-next';

const isLoading = ref(true);
const programmes = ref<any[]>([]);
const summary = ref<any | null>(null);

onMounted(async () => {
  try {
    const res = await enrolmentsApi.getMonitoring();
    programmes.value = res.data.programmes || [];
    summary.value = res.data.summary || null;
  } catch (err) {
    console.error('Failed to load enrolment monitoring', err);
  } finally {
    isLoading.value = false;
  }
});
</script>
