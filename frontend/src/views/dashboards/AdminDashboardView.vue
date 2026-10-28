<template>
  <div class="space-y-6">
    <PageHeader
      title="Regional & Platform Monitoring Overview"
      description="Centralized operational monitoring of affiliated institutions, student verification queues, and duplicate conflicts."
    >
      <template #badge>
        <span class="px-2 py-0.5 rounded-sm bg-primary-soft text-primary font-mono text-[11px] font-semibold border border-primary/20">
          ADMIN ACCESS
        </span>
      </template>
      <template #actions>
        <!-- Compact Contextual Institution Selector (Section 4.2) -->
        <div class="flex items-center gap-2">
          <div class="relative">
            <select
              v-model="selectedQuickInstitution"
              @change="navigateToSelectedInstitution"
              class="h-[36px] pl-3 pr-8 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors focus:outline-none focus:border-primary shadow-subtle cursor-pointer"
            >
              <option value="">Quick Select Institution...</option>
              <option v-for="inst in recentInstitutions" :key="inst.id" :value="inst.id">
                {{ inst.name }} ({{ inst.code }})
              </option>
            </select>
          </div>

          <router-link
            to="/verification"
            class="px-3.5 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
          >
            <ShieldCheck class="w-4 h-4" />
            <span>Verification Queue</span>
          </router-link>
        </div>
      </template>
    </PageHeader>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      <div v-for="i in 6" :key="i" class="h-28 bg-surface rounded-[8px] border border-border animate-pulse p-4"></div>
    </div>

    <!-- KPI Cards Grid (Exact 6 KPIs from Section 10) -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      <MetricCard
        label="Total Institutions"
        :value="kpis.total_institutions || 0"
        subtext="Affiliated technical institutes"
        :icon="Building2"
      />
      <MetricCard
        label="Accessible Student Records"
        :value="kpis.accessible_students || 0"
        subtext="Platform-wide enrolments"
        :icon="Users"
      />
      <MetricCard
        label="Verified Records"
        :value="kpis.verified_records || 0"
        subtext="Confirmed APAAR identities"
        change-text="Verified"
        change-type="positive"
        :icon="ShieldCheck"
      />
      <MetricCard
        label="Pending Verification"
        :value="kpis.pending_verification || 0"
        subtext="Requires automated run"
        change-text="Pending"
        change-type="caution"
        :icon="Clock"
      />
      <MetricCard
        label="Potential Duplicates"
        :value="kpis.potential_duplicates || 0"
        subtext="Cross-institution flags"
        change-text="Review"
        change-type="caution"
        :icon="Copy"
      />
      <MetricCard
        label="Uploads Requiring Attention"
        :value="kpis.uploads_requiring_attention || 0"
        subtext="Batches with row errors"
        change-text="Flagged"
        change-type="negative"
        :icon="AlertTriangle"
      />
    </div>

    <!-- Operational Tables Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Authorized Institutions Operational Entry Point (Section 4.1 & 4.2) -->
      <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
        <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
          <div>
            <h3 class="text-[14px] font-semibold text-text-primary">Affiliated Institutions</h3>
            <p class="text-[11px] text-text-secondary mt-0.5">Select an institution to inspect profile and enrolled students</p>
          </div>
          <span class="text-[11px] font-mono text-text-secondary">
            {{ recentInstitutions.length }} Active
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                <th class="py-2.5 px-4">Code</th>
                <th class="py-2.5 px-4">Institution Name</th>
                <th class="py-2.5 px-4">State</th>
                <th class="py-2.5 px-4">Status</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60 text-[12px]">
              <tr v-for="inst in recentInstitutions" :key="inst.id" class="hover:bg-canvas/50 transition-colors">
                <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ inst.code }}</td>
                <td class="py-3 px-4 font-medium text-text-primary truncate max-w-[180px]">{{ inst.name }}</td>
                <td class="py-3 px-4 text-text-secondary">{{ inst.state }}</td>
                <td class="py-3 px-4">
                  <StatusBadge :status="inst.status" />
                </td>
                <td class="py-3 px-4 text-right">
                  <router-link
                    :to="`/institutions/${inst.id}`"
                    class="px-2.5 py-1 rounded-[4px] bg-canvas hover:bg-border text-primary border border-border font-medium text-[11px] inline-flex items-center gap-1 transition-colors"
                  >
                    <span>View & Students</span>
                    <ArrowRight class="w-3 h-3" />
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Verification Queue Items -->
      <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
        <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
          <div>
            <h3 class="text-[14px] font-semibold text-text-primary">Verification Queue Priority</h3>
            <p class="text-[11px] text-text-secondary mt-0.5">Pending identity verifications across institutions</p>
          </div>
          <router-link to="/verification" class="text-[12px] text-primary hover:underline font-medium">
            Open Queue →
          </router-link>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                <th class="py-2.5 px-4">Student ID</th>
                <th class="py-2.5 px-4">Student Name</th>
                <th class="py-2.5 px-4">APAAR</th>
                <th class="py-2.5 px-4">Status</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60 text-[12px]">
              <tr v-for="s in verificationQueue" :key="s.id" class="hover:bg-canvas/50 transition-colors">
                <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ s.student_id }}</td>
                <td class="py-3 px-4 font-medium text-text-primary">{{ s.student_name }}</td>
                <td class="py-3 px-4 font-mono text-text-secondary">{{ s.apaar_id_masked }}</td>
                <td class="py-3 px-4">
                  <StatusBadge :status="s.verification_status" />
                </td>
                <td class="py-3 px-4 text-right">
                  <router-link
                    :to="`/students/${s.id}`"
                    class="text-primary hover:underline font-medium text-[11px]"
                  >
                    Inspect
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { dashboardApi, institutionsApi, verificationApi } from '@/services/api';
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
  ArrowRight
} from 'lucide-vue-next';

const router = useRouter();

const isLoading = ref(true);
const kpis = ref<any>({});
const recentInstitutions = ref<any[]>([]);
const verificationQueue = ref<any[]>([]);
const selectedQuickInstitution = ref('');

function navigateToSelectedInstitution() {
  if (selectedQuickInstitution.value) {
    router.push(`/institutions/${selectedQuickInstitution.value}`);
  }
}

onMounted(async () => {
  try {
    const [metricsRes, instRes, queueRes] = await Promise.all([
      dashboardApi.getMetrics(),
      institutionsApi.list({ per_page: 6 }),
      verificationApi.getQueue({ per_page: 5 })
    ]);

    kpis.value = metricsRes.data.metrics || {};
    recentInstitutions.value = instRes.data.institutions || [];
    verificationQueue.value = queueRes.data.queue ? queueRes.data.queue.slice(0, 5) : [];
  } catch (err) {
    console.error('Failed to load admin dashboard data', err);
  } finally {
    isLoading.value = false;
  }
});
</script>
