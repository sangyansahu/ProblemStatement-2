<template>
  <div class="space-y-6">
    <!-- Header -->
    <PageHeader
      title="Bulk Student CSV Upload"
      description="Ingest student enrolment records in bulk using standard CSV format with automated row-level validation, duplicate detection, and audit logging."
    >
      <template #actions>
        <a
          href="/api/v1/uploads/template"
          download="aicte_student_upload_template.csv"
          class="px-3.5 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors flex items-center gap-1.5"
        >
          <Download class="w-3.5 h-3.5 text-text-secondary" />
          <span>Download Standard CSV Template</span>
        </a>
      </template>
    </PageHeader>

    <!-- SECTION 1: UPLOAD AREA -->
    <div v-if="!previewData && !importResult" class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle">
      <!-- Drag & Drop Zone -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="[
          'border-2 border-dashed rounded-[8px] p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center',
          isDragging ? 'border-primary bg-primary-soft/30' : 'border-border hover:border-primary/50 bg-[#FAF9F5]'
        ]"
        @click="triggerFileInput"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept=".csv"
          class="hidden"
          @change="handleFileSelect"
        />

        <div class="w-12 h-12 rounded-full bg-primary-soft text-primary flex items-center justify-center mb-3">
          <UploadCloud class="w-6 h-6" />
        </div>

        <div class="text-[15px] font-semibold text-text-primary mb-1">
          Select or drop student enrolment CSV file
        </div>
        <p class="text-[12px] text-text-secondary max-w-md font-normal leading-relaxed">
          Standard CSV with UTF-8 encoding. Maximum file size 16MB (up to 50,000 records). File extension must be <code class="font-mono text-primary font-medium">.csv</code>.
        </p>

        <button
          type="button"
          class="mt-4 px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle"
        >
          Browse Files
        </button>
      </div>

      <!-- Specification Checklist -->
      <div class="mt-6 pt-5 border-t border-border grid grid-cols-1 md:grid-cols-2 gap-4 text-[12px]">
        <div>
          <h4 class="font-semibold text-text-primary mb-2 flex items-center gap-1.5">
            <CheckCircle2 class="w-4 h-4 text-primary" />
            <span>Mandatory Column Headers</span>
          </h4>
          <p class="text-text-secondary leading-relaxed font-mono text-[11px]">
            student_id, student_name, programme_name, branch_or_department, academic_year, enrolment_status
          </p>
        </div>
        <div>
          <h4 class="font-semibold text-text-primary mb-2 flex items-center gap-1.5">
            <ShieldCheck class="w-4 h-4 text-primary" />
            <span>APAAR Identifier Rules</span>
          </h4>
          <p class="text-text-secondary leading-relaxed text-[11px]">
            If supplied, APAAR ID must be exactly 12 numeric digits. Missing APAAR records are flagged as Not Submitted for later assignment.
          </p>
        </div>
      </div>
    </div>

    <!-- PROCESSING LOADER -->
    <div v-if="isValidating" class="bg-surface rounded-[8px] border border-border p-12 text-center shadow-subtle">
      <Loader2 class="w-8 h-8 text-primary animate-spin mx-auto mb-3" />
      <div class="text-[15px] font-semibold text-text-primary">Validating Uploaded File...</div>
      <p class="text-[12px] text-text-secondary mt-1">
        Parsing CSV schema, verifying APAAR identifiers, checking for duplicate student IDs, and cross-institution conflicts.
      </p>
    </div>

    <!-- ERROR BANNER (If header validation failed) -->
    <div
      v-if="validationError"
      class="p-4 rounded-[8px] bg-critical-bg border border-critical/30 text-critical text-[13px] flex items-start justify-between gap-3"
    >
      <div class="flex items-start gap-2.5">
        <AlertTriangle class="w-5 h-5 shrink-0 mt-0.5" />
        <div>
          <strong class="block font-semibold">CSV Validation Error:</strong>
          <span>{{ validationError }}</span>
        </div>
      </div>
      <button
        type="button"
        @click="resetUpload"
        class="text-[12px] underline hover:no-underline font-medium text-critical"
      >
        Try Again
      </button>
    </div>

    <!-- SECTION 2: FILE PREVIEW & VALIDATION SUMMARY -->
    <div v-if="previewData && !importResult" class="space-y-6">
      <!-- File Metadata Strip -->
      <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-md bg-canvas border border-border flex items-center justify-center font-mono text-[11px] font-bold text-primary">
            CSV
          </div>
          <div>
            <div class="font-semibold text-[14px] text-text-primary flex items-center gap-2">
              <span>{{ previewData.file_name }}</span>
              <span class="text-[11px] font-mono text-text-secondary">({{ formatFileSize(previewData.file_size_bytes) }})</span>
            </div>
            <div class="text-[11px] text-text-secondary font-mono mt-0.5">
              Detected {{ previewData.detected_headers?.length }} columns • Header validation:
              <span class="text-success font-semibold">PASSED ✓</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <button
            type="button"
            @click="resetUpload"
            class="px-3 py-1.5 rounded-[6px] bg-surface hover:bg-canvas text-text-secondary hover:text-text-primary border border-border text-[12px] font-medium transition-colors"
          >
            Cancel / Choose Another
          </button>
          <button
            type="button"
            @click="commitImport"
            :disabled="isCommitting || previewData.valid_rows === 0"
            class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5 disabled:opacity-60"
          >
            <Loader2 v-if="isCommitting" class="w-3.5 h-3.5 animate-spin" />
            <span>Commit Valid ({{ previewData.valid_rows }} Records)</span>
          </button>
        </div>
      </div>

      <!-- Validation Summary KPI Cards (Section 12.2 D) -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div class="bg-surface rounded-[6px] border border-border p-3 text-center">
          <span class="text-[11px] text-text-secondary font-medium uppercase tracking-wider block">Total Rows</span>
          <span class="text-[22px] font-semibold text-text-primary font-mono block mt-1">{{ previewData.total_rows }}</span>
        </div>
        <div class="bg-surface rounded-[6px] border border-success/30 bg-success-bg/20 p-3 text-center">
          <span class="text-[11px] text-success font-medium uppercase tracking-wider block">Valid Rows</span>
          <span class="text-[22px] font-semibold text-success font-mono block mt-1">{{ previewData.valid_rows }}</span>
        </div>
        <div class="bg-surface rounded-[6px] border border-critical/30 bg-critical-bg/20 p-3 text-center">
          <span class="text-[11px] text-critical font-medium uppercase tracking-wider block">Invalid Rows</span>
          <span class="text-[22px] font-semibold text-critical font-mono block mt-1">{{ previewData.invalid_rows }}</span>
        </div>
        <div class="bg-surface rounded-[6px] border border-caution/30 bg-caution-bg/20 p-3 text-center">
          <span class="text-[11px] text-caution font-medium uppercase tracking-wider block">Warnings</span>
          <span class="text-[22px] font-semibold text-caution font-mono block mt-1">{{ previewData.warning_rows }}</span>
        </div>
        <div class="bg-surface rounded-[6px] border border-bronze/30 bg-[#FAF4ED] p-3 text-center">
          <span class="text-[11px] text-bronze font-medium uppercase tracking-wider block">Duplicate Flags</span>
          <span class="text-[22px] font-semibold text-bronze font-mono block mt-1">{{ previewData.duplicate_candidates }}</span>
        </div>
        <div class="bg-surface rounded-[6px] border border-border p-3 text-center flex flex-col justify-center">
          <span class="text-[10px] text-text-secondary block">Partial Acceptance</span>
          <span class="text-[11px] text-primary font-semibold block mt-0.5">Valid records imported</span>
        </div>
      </div>

      <!-- Detailed Validation Table (Section 12.2 E) -->
      <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
        <div class="px-5 py-3.5 border-b border-border flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 class="text-[14px] font-semibold text-text-primary">Row-Level Validation Inspection</h3>
            <p class="text-[11px] text-text-secondary mt-0.5">Inspect syntax, APAAR format checks, and duplicate conflict reasons before commit</p>
          </div>

          <!-- Filter Segmented Control -->
          <div class="flex items-center gap-1 p-0.5 rounded-[6px] bg-canvas border border-border text-[11px]">
            <button
              v-for="f in ['all', 'valid', 'invalid', 'warning', 'duplicates']"
              :key="f"
              @click="tableFilter = f"
              :class="[
                'px-2.5 py-1 rounded-[4px] capitalize font-medium transition-colors',
                tableFilter === f ? 'bg-surface text-text-primary border border-border shadow-xs' : 'text-text-secondary hover:text-text-primary'
              ]"
            >
              {{ f }}
            </button>
          </div>
        </div>

        <div class="overflow-x-auto max-h-[460px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <tr>
                <th class="py-2.5 px-3">Row</th>
                <th class="py-2.5 px-3">Student ID</th>
                <th class="py-2.5 px-3">Student Name</th>
                <th class="py-2.5 px-3">APAAR (Masked)</th>
                <th class="py-2.5 px-3">Programme</th>
                <th class="py-2.5 px-3">Validation Status</th>
                <th class="py-2.5 px-4">Issues & Suggested Correction</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60 text-[12px]">
              <tr
                v-for="row in filteredRows"
                :key="row.row_number"
                :class="[
                  'hover:bg-canvas/50 transition-colors',
                  row.status === 'invalid' ? 'bg-critical-bg/15' : row.status === 'warning' ? 'bg-caution-bg/15' : ''
                ]"
              >
                <td class="py-2.5 px-3 font-mono text-[11px] text-text-secondary">{{ row.row_number }}</td>
                <td class="py-2.5 px-3 font-mono font-medium text-text-primary">{{ row.student_id }}</td>
                <td class="py-2.5 px-3 font-medium text-text-primary">{{ row.student_name || '—' }}</td>
                <td class="py-2.5 px-3 font-mono text-text-secondary">{{ row.apaar_id_masked }}</td>
                <td class="py-2.5 px-3 text-text-secondary truncate max-w-[140px]">{{ row.programme_name }}</td>
                <td class="py-2.5 px-3">
                  <StatusBadge :status="row.status" />
                </td>
                <td class="py-2.5 px-4 text-[11px]">
                  <template v-if="row.errors && row.errors.length > 0">
                    <div v-for="(err, idx) in row.errors" :key="idx" class="text-critical leading-tight mb-1">
                      <strong>{{ err.field }}:</strong> {{ err.message }}
                      <span v-if="err.suggestion" class="text-text-secondary block text-[10px]">
                        Suggestion: {{ err.suggestion }}
                      </span>
                    </div>
                  </template>
                  <template v-else-if="row.warnings && row.warnings.length > 0">
                    <div v-for="(w, idx) in row.warnings" :key="idx" class="text-caution leading-tight mb-1">
                      <strong>{{ w.field }}:</strong> {{ w.message }}
                    </div>
                  </template>
                  <span v-else class="text-success font-medium">✓ Valid</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- SECTION 3: IMPORT COMPLETION REPORT (Section 12.2 G) -->
    <div v-if="importResult" class="bg-surface rounded-[8px] border border-border p-6 sm:p-8 shadow-subtle space-y-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-success-bg text-success border border-success/30 flex items-center justify-center shrink-0">
          <CheckCircle2 class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-[18px] font-semibold text-text-primary">
            CSV Import Batch Committed Successfully
          </h2>
          <p class="text-[12px] text-text-secondary mt-0.5 font-mono">
            Batch Reference ID: <strong class="text-text-primary font-bold">{{ importResult.batch_id }}</strong>
          </p>
        </div>
      </div>

      <!-- Outcome Stats -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-[6px] bg-canvas border border-border">
        <div>
          <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Total Processed</span>
          <span class="text-[20px] font-mono font-semibold text-text-primary block mt-0.5">{{ importResult.total_processed }}</span>
        </div>
        <div>
          <span class="text-[11px] text-success uppercase tracking-wider block">Successfully Imported</span>
          <span class="text-[20px] font-mono font-semibold text-success block mt-0.5">{{ importResult.imported_count }}</span>
        </div>
        <div>
          <span class="text-[11px] text-critical uppercase tracking-wider block">Rejected / Invalid</span>
          <span class="text-[20px] font-mono font-semibold text-critical block mt-0.5">{{ importResult.rejected_count }}</span>
        </div>
        <div>
          <span class="text-[11px] text-bronze uppercase tracking-wider block">Duplicate Conflicts</span>
          <span class="text-[20px] font-mono font-semibold text-bronze block mt-0.5">{{ importResult.duplicate_candidates }}</span>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-border">
        <div class="text-[12px] text-text-secondary">
          Completed at: <span class="font-mono">{{ formatDate(importResult.completed_at) }}</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            type="button"
            @click="resetUpload"
            class="px-4 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors"
          >
            Upload Another Batch
          </button>
          <router-link
            to="/students"
            class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle"
          >
            View Student Directory →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { uploadsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import {
  UploadCloud,
  Download,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Loader2
} from 'lucide-vue-next';

const fileInputRef = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const isValidating = ref(false);
const isCommitting = ref(false);

const validationError = ref<string | null>(null);
const previewData = ref<any | null>(null);
const importResult = ref<any | null>(null);
const tableFilter = ref('all');

function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    processFile(target.files[0]);
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    processFile(e.dataTransfer.files[0]);
  }
}

async function processFile(file: File) {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    validationError.value = 'Only .csv format files are accepted.';
    return;
  }

  validationError.value = null;
  isValidating.value = true;
  previewData.value = null;
  importResult.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await uploadsApi.previewCsv(formData);
    previewData.value = res.data;
  } catch (err: any) {
    validationError.value = err.response?.data?.error || 'Failed to parse and validate CSV file.';
  } finally {
    isValidating.value = false;
  }
}

const filteredRows = computed(() => {
  if (!previewData.value?.row_results) return [];
  const rows = previewData.value.row_results;
  if (tableFilter.value === 'valid') return rows.filter((r: any) => r.status === 'valid');
  if (tableFilter.value === 'invalid') return rows.filter((r: any) => r.status === 'invalid');
  if (tableFilter.value === 'warning') return rows.filter((r: any) => r.status === 'warning');
  if (tableFilter.value === 'duplicates') {
    return rows.filter((r: any) => (r.errors?.some((e: any) => e.field === 'student_id' || e.field === 'apaar_id')) || r.warnings?.some((w: any) => w.field === 'apaar_id'));
  }
  return rows;
});

async function commitImport() {
  if (!previewData.value) return;

  const confirmMsg = `Confirm committing ${previewData.value.valid_rows} valid student records into the database? Invalid rows (${previewData.value.invalid_rows}) will be rejected.`;
  if (!window.confirm(confirmMsg)) return;

  isCommitting.value = true;
  try {
    const res = await uploadsApi.commitCsv({
      file_name: previewData.value.file_name,
      file_size_bytes: previewData.value.file_size_bytes,
      row_results: previewData.value.row_results
    });
    importResult.value = res.data;
    previewData.value = null;
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to commit import records');
  } finally {
    isCommitting.value = false;
  }
}

function resetUpload() {
  previewData.value = null;
  importResult.value = null;
  validationError.value = null;
  if (fileInputRef.value) fileInputRef.value.value = '';
}

function formatFileSize(bytes: number) {
  if (!bytes) return '0 KB';
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function formatDate(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-IN');
}
</script>
