<template>
  <div class="space-y-6">
    <PageHeader
      title="National Administrative Executive Dashboard"
      description="Full system governance, institutional compliance monitoring, APAAR identity registry synchronization, and security audit logs."
    >
      <template #badge>
        <span class="px-2 py-0.5 rounded-sm bg-critical-bg text-critical font-mono text-[11px] font-semibold border border-critical/20">
          SUPER ADMIN
        </span>
      </template>
      <template #actions>
        <router-link
          to="/duplicate-review"
          class="px-3.5 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors flex items-center gap-1.5"
        >
          <Copy class="w-3.5 h-3.5 text-text-secondary" />
          <span>Resolve Conflicts</span>
        </router-link>
        <button
          type="button"
          @click="runBatchVerification"
          :disabled="isBatchVerifying"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5 disabled:opacity-70"
        >
          <Play v-if="!isBatchVerifying" class="w-4 h-4" />
          <Loader2 v-else class="w-4 h-4 animate-spin" />
          <span>{{ isBatchVerifying ? 'Running Verification...' : 'Run Automated Batch Verification' }}</span>
        </button>
      </template>
    </PageHeader>

    <!-- Top Status Banner -->
    <div class="bg-[#FAF9F5] border border-border rounded-[8px] p-3.5 flex flex-wrap items-center justify-between gap-3 text-[12px]">
      <div class="flex items-center gap-2.5">
        <span class="w-2.5 h-2.5 rounded-full bg-success"></span>
        <span class="font-semibold text-text-primary">System Integrity Normal</span>
        <span class="text-text-secondary">|</span>
        <span class="text-text-secondary">Database: PostgreSQL Compatible Engine</span>
        <span class="text-text-secondary">|</span>
        <span class="text-text-secondary">APAAR Encryption: AES-256 + SHA-256 Keyed HMAC</span>
      </div>
      <div class="flex items-center gap-2 font-mono text-[11px] text-text-secondary">
        <span>Adapter: Simulated Educational Registry Sandbox</span>
      </div>
    </div>

    <!-- KPI Grid (Exact 8 KPIs from Section 11) -->
    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="h-28 bg-surface rounded-[8px] border border-border animate-pulse p-4"></div>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        label="Total Institutions"
        :value="kpis.total_institutions || 0"
        subtext="Registered educational bodies"
        :icon="Building2"
      />
      <MetricCard
        label="Active Institution Accounts"
        :value="kpis.active_institutions || 0"
        subtext="Operating without restriction"
        change-text="Operational"
        change-type="positive"
        :icon="CheckCircle2"
      />
      <MetricCard
        label="Total Student Records"
        :value="kpis.total_students || 0"
        subtext="Enrolled across institutions"
        :icon="Users"
      />
      <MetricCard
        label="Verified Records"
        :value="kpis.verified_records || 0"
        subtext="Officially confirmed APAAR"
        change-text="Verified"
        change-type="positive"
        :icon="ShieldCheck"
      />
      <MetricCard
        label="Pending Verification"
        :value="kpis.pending_verification || 0"
        subtext="Awaiting scheduled run"
        change-text="Pending"
        change-type="caution"
        :icon="Clock"
      />
      <MetricCard
        label="Potential Duplicate Conflicts"
        :value="kpis.potential_duplicate_conflicts || 0"
        subtext="Cross-bureau / institution overlaps"
        change-text="Action Required"
        change-type="caution"
        :icon="Copy"
      />
      <MetricCard
        label="Failed Import Batches"
        :value="kpis.failed_import_batches || 0"
        subtext="Batches rejected by schema"
        :change-text="kpis.failed_import_batches > 0 ? 'Critical' : 'None'"
        :change-type="kpis.failed_import_batches > 0 ? 'negative' : 'positive'"
        :icon="AlertTriangle"
      />
      <MetricCard
        label="Records Requiring Review"
        :value="kpis.records_requiring_review || 0"
        subtext="Discrepancy / manual review"
        change-text="Needs Attention"
        change-type="negative"
        :icon="Scale"
      />
    </div>

    <!-- Duplicate Conflicts & Recent Activity Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Duplicate Conflicts Queue (2 cols) -->
      <div class="lg:col-span-2 bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
        <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
          <div>
            <h3 class="text-[14px] font-semibold text-text-primary">Cross-Institution Conflict Queue</h3>
            <p class="text-[11px] text-text-secondary mt-0.5">Flagged duplicate student records and transfer overlaps</p>
          </div>
          <router-link to="/duplicate-review" class="text-[12px] text-primary hover:underline font-medium">
            Full Review Panel →
          </router-link>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                <th class="py-2.5 px-4">Case Ref</th>
                <th class="py-2.5 px-4">Issue Type</th>
                <th class="py-2.5 px-4">Student</th>
                <th class="py-2.5 px-4">Severity</th>
                <th class="py-2.5 px-4">Status</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60 text-[12px]">
              <tr v-if="duplicateCases.length === 0">
                <td colspan="6" class="p-4 text-center text-text-secondary">
                  No active duplicate conflicts detected across institutions.
                </td>
              </tr>
              <tr v-for="c in duplicateCases" :key="c.id" class="hover:bg-canvas/50 transition-colors">
                <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ c.case_reference }}</td>
                <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">{{ c.issue_type }}</td>
                <td class="py-3 px-4">
                  <div class="font-medium text-text-primary">{{ c.student_name }}</div>
                  <div class="font-mono text-[11px] text-text-secondary">{{ c.student_id }}</div>
                </td>
                <td class="py-3 px-4">
                  <span
                    :class="[
                      'text-[10px] font-mono px-2 py-0.5 rounded-sm uppercase font-semibold border',
                      c.severity === 'critical' ? 'bg-critical-bg text-critical border-critical/20' : 'bg-caution-bg text-caution border-caution/20'
                    ]"
                  >
                    {{ c.severity }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <StatusBadge :status="c.status" />
                </td>
                <td class="py-3 px-4 text-right">
                  <router-link to="/duplicate-review" class="text-primary hover:underline font-medium text-[11px]">
                    Resolve Case
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent System Audit Actions (1 col) -->
      <div class="bg-surface rounded-[8px] border border-border shadow-subtle flex flex-col">
        <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
          <div>
            <h3 class="text-[14px] font-semibold text-text-primary">System Audit Trail</h3>
            <p class="text-[11px] text-text-secondary mt-0.5">Recent administrative events</p>
          </div>
          <router-link to="/audit-logs" class="text-[12px] text-primary hover:underline font-medium">
            All Logs →
          </router-link>
        </div>

        <div class="p-4 divide-y divide-border/60 flex-1 overflow-y-auto max-h-[420px]">
          <div v-for="log in recentActivity" :key="log.id" class="py-2.5 text-[12px]">
            <div class="flex items-center justify-between font-mono text-[10px] text-text-secondary">
              <span class="font-semibold text-text-primary">{{ log.action }}</span>
              <span>{{ formatDate(log.created_at) }}</span>
            </div>
            <div class="text-[11px] text-text-secondary mt-1">
              By <strong class="text-text-primary">{{ log.actor_name }}</strong> ({{ log.actor_role }})
            </div>
            <div class="font-mono text-[10px] text-text-secondary/80 mt-0.5 truncate">
              Target: {{ log.target_type }} {{ log.target_id || '' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { dashboardApi, verificationApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import MetricCard from '@/components/common/MetricCard.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import {
  Building2,
  Users,
  ShieldCheck,
  Clock,
  Copy,
  AlertTriangle,
  Scale,
  CheckCircle2,
  Play,
  Loader2
} from 'lucide-vue-next';

const isLoading = ref(true);
const isBatchVerifying = ref(false);

const kpis = ref<any>({});
const duplicateCases = ref<any[]>([]);
const recentActivity = ref<any[]>([]);

function formatDate(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function runBatchVerification() {
  isBatchVerifying.value = true;
  try {
    const res = await verificationApi.batchVerify();
    alert(`Batch Verification Complete: ${res.data.verified_count} verified, ${res.data.flagged_count} flagged for review.`);
    loadMetrics();
  } catch (err: any) {
    alert(err.response?.data?.message || 'Verification batch failed');
  } finally {
    isBatchVerifying.value = false;
  }
}

async function loadMetrics() {
  try {
    const res = await dashboardApi.getMetrics();
    kpis.value = res.data.kpis || {};
    duplicateCases.value = res.data.duplicate_cases || [];
    recentActivity.value = res.data.recent_activity || [];
  } catch (err) {
    console.error('Failed to load super admin dashboard', err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadMetrics();
});
</script>
