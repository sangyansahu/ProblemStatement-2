<template>
  <div class="space-y-6">
    <PageHeader
      title="Reports & Institutional Analytics"
      description="Downloadable compliance reports, verification progress audits, and programme capacity utilization analytics."
    />

    <!-- Summary KPI Strip -->
    <div v-if="overview" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Total Students Registered</span>
        <span class="text-[24px] font-semibold text-text-primary font-mono block mt-1">{{ overview.total_students }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-success uppercase tracking-wider block">Identity Verified</span>
        <span class="text-[24px] font-semibold text-success font-mono block mt-1">{{ overview.verified_records }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-caution uppercase tracking-wider block">Pending Verification</span>
        <span class="text-[24px] font-semibold text-caution font-mono block mt-1">{{ overview.pending_records }}</span>
      </div>
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle">
        <span class="text-[11px] text-primary uppercase tracking-wider block">Verification Rate</span>
        <span class="text-[24px] font-semibold text-primary font-mono block mt-1">{{ overview.verification_rate }}%</span>
      </div>
    </div>

    <!-- Downloadable Standard Reports Cards (Section 18) -->
    <div class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle">
      <h3 class="text-[15px] font-semibold text-text-primary mb-1">Official Downloadable CSV Reports</h3>
      <p class="text-[12px] text-text-secondary mb-5">
        Export authorized datasets adhering to AICTE data protection policy. Sensitive APAAR identifiers are masked.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Verification Report -->
        <div class="p-4 rounded-[6px] border border-border bg-[#FAF9F5] flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2 font-semibold text-[13px] text-text-primary">
              <FileSpreadsheet class="w-4 h-4 text-primary" />
              <span>Student Verification Audit</span>
            </div>
            <p class="text-[11px] text-text-secondary leading-relaxed">
              Complete status report of all enrolled students, verification outcomes, timestamp, and review annotations.
            </p>
          </div>
          <button
            type="button"
            @click="downloadReport('verification')"
            class="mt-4 px-3 py-1.5 rounded-[4px] bg-primary text-[#FFFEFA] hover:bg-primary-hover text-[11px] font-medium flex items-center justify-center gap-1.5 shadow-subtle"
          >
            <Download class="w-3.5 h-3.5" />
            <span>Download CSV</span>
          </button>
        </div>

        <!-- Duplicates Report -->
        <div class="p-4 rounded-[6px] border border-border bg-[#FAF9F5] flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2 font-semibold text-[13px] text-text-primary">
              <Copy class="w-4 h-4 text-caution" />
              <span>Duplicate Conflicts Audit</span>
            </div>
            <p class="text-[11px] text-text-secondary leading-relaxed">
              Detailed registry of cross-institution student ID collisions, duplicate APAAR detections, and resolution findings.
            </p>
          </div>
          <button
            type="button"
            @click="downloadReport('duplicates')"
            class="mt-4 px-3 py-1.5 rounded-[4px] bg-surface hover:bg-canvas text-text-primary border border-border text-[11px] font-medium flex items-center justify-center gap-1.5"
          >
            <Download class="w-3.5 h-3.5" />
            <span>Download CSV</span>
          </button>
        </div>

        <!-- Intake Report -->
        <div class="p-4 rounded-[6px] border border-border bg-[#FAF9F5] flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2 font-semibold text-[13px] text-text-primary">
              <Scale class="w-4 h-4 text-primary" />
              <span>Intake & Enrolment Utilization</span>
            </div>
            <p class="text-[11px] text-text-secondary leading-relaxed">
              Programme-wise comparison of approved intake capacity against active enrolments with discrepancy flags.
            </p>
          </div>
          <button
            type="button"
            @click="downloadReport('intake')"
            class="mt-4 px-3 py-1.5 rounded-[4px] bg-surface hover:bg-canvas text-text-primary border border-border text-[11px] font-medium flex items-center justify-center gap-1.5"
          >
            <Download class="w-3.5 h-3.5" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Programme Enrolment Breakdown -->
    <div class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle">
      <h3 class="text-[14px] font-semibold text-text-primary mb-1">Enrolment Breakdown by Programme</h3>
      <p class="text-[11px] text-text-secondary mb-4">Distribution of active students across technical disciplines</p>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="prog in byProgramme"
          :key="prog.programme"
          class="p-3 rounded-[6px] bg-canvas border border-border flex items-center justify-between text-[12px]"
        >
          <span class="font-medium text-text-primary truncate max-w-[200px]">{{ prog.programme }}</span>
          <span class="font-mono font-semibold text-primary px-2 py-0.5 rounded-sm bg-primary-soft">{{ prog.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { reportsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import { FileSpreadsheet, Copy, Scale, Download } from 'lucide-vue-next';

const isLoading = ref(true);
const overview = ref<any | null>(null);
const byProgramme = ref<any[]>([]);

async function fetchReports() {
  isLoading.value = true;
  try {
    const res = await reportsApi.getSummary();
    overview.value = res.data.overview;
    byProgramme.value = res.data.by_programme || [];
  } catch (err) {
    console.error('Failed to load reports', err);
  } finally {
    isLoading.value = false;
  }
}

async function downloadReport(type: string) {
  try {
    const res = await reportsApi.exportCsv(type);
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${type}_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    alert(`Failed to export ${type} report`);
  }
}

onMounted(() => {
  fetchReports();
});
</script>
