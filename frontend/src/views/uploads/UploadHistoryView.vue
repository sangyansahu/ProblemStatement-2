<template>
  <div class="space-y-6">
    <PageHeader
      title="CSV Ingest & Batch Upload History"
      description="Historical record of all bulk student enrolment CSV submissions with detailed row-level error breakdowns."
    >
      <template #actions>
        <router-link
          to="/bulk-upload"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <UploadCloud class="w-4 h-4" />
          <span>New CSV Ingest</span>
        </router-link>
      </template>
    </PageHeader>

    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Batch ID</th>
              <th class="py-2.5 px-4">File Name</th>
              <th v-if="!authStore.isInstitute" class="py-2.5 px-4">Institution</th>
              <th class="py-2.5 px-4">Total Rows</th>
              <th class="py-2.5 px-4">Valid / Committed</th>
              <th class="py-2.5 px-4">Errors</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4">Upload Date</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="9" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading upload history...</span>
              </td>
            </tr>
            <tr v-else-if="batches.length === 0">
              <td colspan="9" class="p-8 text-center text-text-secondary">
                No upload batches recorded yet.
              </td>
            </tr>
            <tr v-for="b in batches" :key="b.id" class="hover:bg-canvas/50 transition-colors">
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ b.batch_id }}</td>
              <td class="py-3 px-4 truncate max-w-[180px] text-text-primary font-medium">{{ b.file_name }}</td>
              <td v-if="!authStore.isInstitute" class="py-3 px-4 text-text-secondary truncate max-w-[150px]">
                {{ b.institution_name }}
              </td>
              <td class="py-3 px-4 font-mono text-text-secondary">{{ b.total_rows }}</td>
              <td class="py-3 px-4 font-mono font-semibold text-success">{{ b.valid_rows }}</td>
              <td class="py-3 px-4 font-mono">
                <span v-if="b.invalid_rows > 0" class="text-critical font-semibold">
                  {{ b.invalid_rows }}
                </span>
                <span v-else class="text-text-secondary">0</span>
              </td>
              <td class="py-3 px-4">
                <StatusBadge :status="b.status" />
              </td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">
                {{ formatDate(b.created_at) }}
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    v-if="b.invalid_rows > 0"
                    type="button"
                    @click="viewErrorReport(b.id)"
                    class="text-[11px] text-primary hover:underline font-medium"
                  >
                    View Errors
                  </button>
                  <a
                    v-if="b.invalid_rows > 0"
                    :href="`/api/v1/uploads/batches/${b.id}/error-report`"
                    class="p-1 rounded-sm text-text-secondary hover:text-text-primary hover:bg-canvas"
                    title="Download Error Report CSV"
                  >
                    <Download class="w-3.5 h-3.5" />
                  </a>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ERROR REPORT MODAL -->
    <ModalDialog
      :open="openErrorModal"
      :title="`Error Report - ${selectedBatch?.batch_id || ''}`"
      max-width="2xl"
      @close="openErrorModal = false"
    >
      <div v-if="selectedBatch" class="space-y-4">
        <div class="p-3 bg-canvas rounded-[6px] border border-border text-[12px] flex items-center justify-between">
          <div>
            <span>File: <strong class="text-text-primary">{{ selectedBatch.file_name }}</strong></span>
            <span class="text-text-secondary ml-3">({{ selectedBatch.invalid_rows }} rejected rows)</span>
          </div>
          <a
            :href="`/api/v1/uploads/batches/${selectedBatch.id}/error-report`"
            class="px-2.5 py-1 rounded-[4px] bg-surface hover:bg-canvas text-primary border border-primary/30 text-[11px] font-medium flex items-center gap-1"
          >
            <Download class="w-3 h-3" />
            <span>Export CSV Report</span>
          </a>
        </div>

        <div class="max-h-80 overflow-y-auto overflow-x-auto border border-border rounded-[6px]">
          <table class="w-full text-left border-collapse text-[12px]">
            <thead class="sticky top-0 bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase">
              <tr>
                <th class="py-2 px-3">Row</th>
                <th class="py-2 px-3">Student ID</th>
                <th class="py-2 px-3">Field</th>
                <th class="py-2 px-3">Error Description</th>
                <th class="py-2 px-3">Suggested Correction</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60">
              <tr v-for="(err, idx) in selectedBatch.error_report" :key="idx" class="hover:bg-canvas/50">
                <td class="py-2 px-3 font-mono text-[11px] text-text-secondary">{{ err.row_number }}</td>
                <td class="py-2 px-3 font-mono font-medium text-text-primary">{{ err.student_id }}</td>
                <td class="py-2 px-3 font-mono text-critical text-[11px]">{{ err.field }}</td>
                <td class="py-2 px-3 text-text-primary leading-tight">{{ err.error }}</td>
                <td class="py-2 px-3 text-text-secondary text-[11px]">{{ err.suggestion || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="openErrorModal = false"
          class="px-4 py-1.5 rounded-[6px] bg-primary text-[#FFFEFA] text-[12px] font-medium"
        >
          Close
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { uploadsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import {
  UploadCloud,
  Download,
  Loader2
} from 'lucide-vue-next';

const authStore = useAuthStore();
const isLoading = ref(true);
const batches = ref<any[]>([]);

const openErrorModal = ref(false);
const selectedBatch = ref<any | null>(null);

function formatDate(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function fetchBatches() {
  isLoading.value = true;
  try {
    const res = await uploadsApi.listBatches();
    batches.value = res.data.batches || [];
  } catch (err) {
    console.error('Failed to load batches', err);
  } finally {
    isLoading.value = false;
  }
}

async function viewErrorReport(batchId: number) {
  try {
    const res = await uploadsApi.getBatch(batchId);
    selectedBatch.value = res.data.batch;
    openErrorModal.value = true;
  } catch (err) {
    alert('Failed to load error report');
  }
}

onMounted(() => {
  fetchBatches();
});
</script>
