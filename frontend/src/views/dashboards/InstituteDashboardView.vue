<template>
  <div class="space-y-6">
    <!-- Page Header with Institution Context & Quick Actions -->
    <PageHeader
      title="Institution Overview"
      :description="`Operational management of student enrolment and verification records for ${authStore.user?.institution_name || 'your institution'}.`"
    >
      <template #badge>
        <span class="px-2 py-0.5 rounded-sm bg-primary-soft text-primary font-mono text-[11px] font-semibold border border-primary/20">
          {{ authStore.user?.institution_code || 'INST-CODE' }}
        </span>
      </template>
      <template #actions>
        <a
          href="/api/v1/uploads/template"
          download="aicte_student_upload_template.csv"
          class="px-3.5 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors flex items-center gap-1.5"
        >
          <Download class="w-3.5 h-3.5 text-text-secondary" />
          <span>Download CSV Template</span>
        </a>
        <router-link
          to="/bulk-upload"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <UploadCloud class="w-4 h-4" />
          <span>Upload Student CSV</span>
        </router-link>
      </template>
    </PageHeader>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      <div v-for="i in 6" :key="i" class="h-28 bg-surface rounded-[8px] border border-border animate-pulse p-4"></div>
    </div>

    <!-- KPI Cards Grid (Exact 6 KPIs from Section 9) -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      <MetricCard
        label="Total Student Records"
        :value="kpis.total_students || 0"
        subtext="Enrolled across all branches"
        :icon="Users"
      />
      <MetricCard
        label="Verified Records"
        :value="kpis.verified_records || 0"
        subtext="APAAR identity confirmed"
        change-text="Active"
        change-type="positive"
        :icon="ShieldCheck"
      />
      <MetricCard
        label="Pending Verification"
        :value="kpis.pending_verification || 0"
        subtext="In verification queue"
        change-text="Pending"
        change-type="caution"
        :icon="Clock"
      />
      <MetricCard
        label="Invalid Records"
        :value="kpis.invalid_records || 0"
        subtext="Requires correction"
        change-text="Action Needed"
        change-type="negative"
        :icon="AlertTriangle"
      />
      <MetricCard
        label="Duplicate Candidates"
        :value="kpis.duplicate_candidates || 0"
        subtext="Conflicts under review"
        change-text="Discrepancy"
        change-type="caution"
        :icon="Copy"
      />
      <MetricCard
        label="Recent Upload Status"
        :value="kpis.recent_upload_status || 'N/A'"
        :subtext="`Batch: ${kpis.recent_upload_batch || 'None'}`"
        :icon="CheckCircle2"
      />
    </div>

    <!-- Two-Column Operational Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column (2 spans): Recent Uploads & Records Requiring Attention -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Recent Uploads Table -->
        <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
            <div>
              <h3 class="text-[14px] font-semibold text-text-primary">Recent CSV Uploads</h3>
              <p class="text-[11px] text-text-secondary mt-0.5">Most recent batch submissions for your institution</p>
            </div>
            <router-link to="/upload-history" class="text-[12px] text-primary hover:underline font-medium">
              View All History →
            </router-link>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                  <th class="py-2.5 px-4">Batch ID</th>
                  <th class="py-2.5 px-4">File Name</th>
                  <th class="py-2.5 px-4">Valid / Total</th>
                  <th class="py-2.5 px-4">Errors</th>
                  <th class="py-2.5 px-4">Status</th>
                  <th class="py-2.5 px-4 text-right">Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 text-[12px]">
                <tr v-if="recentUploads.length === 0">
                  <td colspan="6" class="p-4 text-center text-text-secondary">
                    No upload batches recorded yet. Upload student CSV to begin.
                  </td>
                </tr>
                <tr
                  v-for="b in recentUploads"
                  :key="b.id"
                  class="hover:bg-canvas/50 transition-colors"
                >
                  <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ b.batch_id }}</td>
                  <td class="py-3 px-4 truncate max-w-[180px] text-text-secondary">{{ b.file_name }}</td>
                  <td class="py-3 px-4 font-mono text-text-primary">{{ b.valid_rows }} / {{ b.total_rows }}</td>
                  <td class="py-3 px-4">
                    <span v-if="b.invalid_rows > 0" class="text-critical font-mono font-semibold">
                      {{ b.invalid_rows }}
                    </span>
                    <span v-else class="text-text-secondary font-mono">0</span>
                  </td>
                  <td class="py-3 px-4">
                    <StatusBadge :status="b.status" />
                  </td>
                  <td class="py-3 px-4 text-right font-mono text-[11px] text-text-secondary">
                    {{ formatDate(b.created_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Student Records Requiring Correction -->
        <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
            <div>
              <h3 class="text-[14px] font-semibold text-text-primary">Records Requiring Correction</h3>
              <p class="text-[11px] text-text-secondary mt-0.5">Students with flagged demographic or APAAR format discrepancies</p>
            </div>
            <router-link to="/verification" class="text-[12px] text-primary hover:underline font-medium">
              Verification Queue →
            </router-link>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                  <th class="py-2.5 px-4">Student ID</th>
                  <th class="py-2.5 px-4">Student Name</th>
                  <th class="py-2.5 px-4">Programme</th>
                  <th class="py-2.5 px-4">Issue Description</th>
                  <th class="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 text-[12px]">
                <tr v-if="correctionNeeded.length === 0">
                  <td colspan="5" class="p-4 text-center text-success font-medium">
                    ✓ All student records currently meet validation requirements.
                  </td>
                </tr>
                <tr
                  v-for="s in correctionNeeded"
                  :key="s.id"
                  class="hover:bg-canvas/50 transition-colors"
                >
                  <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ s.student_id }}</td>
                  <td class="py-3 px-4 font-medium text-text-primary">{{ s.student_name }}</td>
                  <td class="py-3 px-4 text-text-secondary truncate max-w-[140px]">{{ s.programme_name }}</td>
                  <td class="py-3 px-4 text-critical text-[11px] truncate max-w-[200px]" :title="s.verification_notes">
                    {{ s.verification_notes || 'Demographic discrepancy' }}
                  </td>
                  <td class="py-3 px-4 text-right">
                    <router-link
                      :to="`/students/${s.id}`"
                      class="text-primary hover:underline font-medium text-[11px]"
                    >
                      Correct Record
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: Verification Breakdown & Potential Duplicates -->
      <div class="space-y-6">
        <!-- Verification Status Distribution -->
        <div class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle">
          <h3 class="text-[14px] font-semibold text-text-primary mb-1">Verification Status Summary</h3>
          <p class="text-[11px] text-text-secondary mb-4">Breakdown of student identity checks</p>

          <div class="space-y-3 font-mono text-[12px]">
            <div>
              <div class="flex justify-between text-text-secondary mb-1">
                <span>Verified</span>
                <span class="font-semibold text-success">{{ verificationDistribution.verified || 0 }}</span>
              </div>
              <div class="w-full h-2 bg-canvas rounded-full overflow-hidden">
                <div
                  class="h-full bg-success rounded-full"
                  :style="{ width: `${getPercentage(verificationDistribution.verified)}%` }"
                ></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-text-secondary mb-1">
                <span>Pending Verification</span>
                <span class="font-semibold text-caution">{{ verificationDistribution.pending || 0 }}</span>
              </div>
              <div class="w-full h-2 bg-canvas rounded-full overflow-hidden">
                <div
                  class="h-full bg-caution rounded-full"
                  :style="{ width: `${getPercentage(verificationDistribution.pending)}%` }"
                ></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-text-secondary mb-1">
                <span>Discrepancy / Mismatch</span>
                <span class="font-semibold text-critical">{{ verificationDistribution.mismatch || 0 }}</span>
              </div>
              <div class="w-full h-2 bg-canvas rounded-full overflow-hidden">
                <div
                  class="h-full bg-critical rounded-full"
                  :style="{ width: `${getPercentage(verificationDistribution.mismatch)}%` }"
                ></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-text-secondary mb-1">
                <span>Not Submitted</span>
                <span class="font-semibold text-[#7E8B87]">{{ verificationDistribution.not_submitted || 0 }}</span>
              </div>
              <div class="w-full h-2 bg-canvas rounded-full overflow-hidden">
                <div
                  class="h-full bg-[#7E8B87] rounded-full"
                  :style="{ width: `${getPercentage(verificationDistribution.not_submitted)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Potential Duplicate Records Alert Box -->
        <div class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-[14px] font-semibold text-text-primary">Potential Duplicate Cases</h3>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-caution-bg text-caution border border-caution/20 font-semibold">
              {{ openDuplicates.length }} OPEN
            </span>
          </div>

          <div v-if="openDuplicates.length === 0" class="text-[12px] text-text-secondary p-3 text-center bg-canvas rounded-[6px]">
            No active duplicate conflicts detected.
          </div>
          <div v-else class="space-y-2.5">
            <div
              v-for="d in openDuplicates"
              :key="d.id"
              class="p-3 rounded-[6px] bg-[#FAF9F5] border border-border text-[12px]"
            >
              <div class="flex items-center justify-between font-mono text-[11px] text-text-secondary">
                <span class="font-semibold text-text-primary">{{ d.case_reference }}</span>
                <span class="text-caution font-medium capitalize">{{ d.severity }}</span>
              </div>
              <div class="font-medium text-text-primary mt-1">{{ d.student_name }} ({{ d.student_id }})</div>
              <p class="text-[11px] text-text-secondary mt-1 line-clamp-2 leading-relaxed">
                {{ d.description }}
              </p>
              <div class="mt-2 text-right">
                <router-link :to="`/duplicate-review`" class="text-primary hover:underline text-[11px] font-medium">
                  Review Case →
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { dashboardApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import MetricCard from '@/components/common/MetricCard.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import {
  Users,
  ShieldCheck,
  Clock,
  AlertTriangle,
  Copy,
  CheckCircle2,
  UploadCloud,
  Download
} from 'lucide-vue-next';

const authStore = useAuthStore();
const isLoading = ref(true);

const kpis = ref<any>({});
const recentUploads = ref<any[]>([]);
const correctionNeeded = ref<any[]>([]);
const openDuplicates = ref<any[]>([]);
const verificationDistribution = ref<any>({});

function formatDate(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
}

function getPercentage(val: number) {
  const total = kpis.value.total_students || 1;
  return Math.min(100, Math.round(((val || 0) / total) * 100));
}

onMounted(async () => {
  try {
    const res = await dashboardApi.getMetrics();
    kpis.value = res.data.kpis || {};
    recentUploads.value = res.data.recent_uploads || [];
    correctionNeeded.value = res.data.records_requiring_correction || [];
    openDuplicates.value = res.data.open_duplicates || [];
    verificationDistribution.value = res.data.verification_distribution || {};
  } catch (err) {
    console.error('Failed to load institute dashboard metrics', err);
  } finally {
    isLoading.value = false;
  }
});
</script>
