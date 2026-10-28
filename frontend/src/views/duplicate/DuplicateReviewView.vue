<template>
  <div class="space-y-6">
    <PageHeader
      title="Duplicate & Cross-Institution Conflict Review"
      description="Queue of conflicting student identifiers, duplicate APAAR detections, and transfer overlap cases requiring authorized administrative resolution."
    />

    <!-- Notice -->
    <div class="p-3.5 rounded-[8px] bg-[#FAF9F5] border border-border text-[12px] text-text-secondary flex items-start gap-2.5">
      <Info class="w-4 h-4 text-text-secondary shrink-0 mt-0.5" />
      <div>
        A duplicate match does not automatically imply regulatory violation or fraud. The system accommodates legitimate lateral transfers, re-admissions, and historical records. Formal decisions require documented explanations.
      </div>
    </div>

    <!-- Conflicts Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Case Reference</th>
              <th class="py-2.5 px-4">Issue Type</th>
              <th class="py-2.5 px-4">Primary Institution</th>
              <th class="py-2.5 px-4">Secondary / Conflicting Institution</th>
              <th class="py-2.5 px-4">Student</th>
              <th class="py-2.5 px-4">Severity</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="8" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading conflict cases...</span>
              </td>
            </tr>
            <tr v-else-if="cases.length === 0">
              <td colspan="8" class="p-8 text-center text-success font-medium">
                ✓ No active duplicate or cross-institution conflict cases.
              </td>
            </tr>
            <tr v-for="c in cases" :key="c.id" class="hover:bg-canvas/50 transition-colors">
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ c.case_reference }}</td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">{{ c.issue_type }}</td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary">{{ c.institution_name }}</div>
                <div class="font-mono text-[11px] text-text-secondary">({{ c.institution_code }})</div>
              </td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary">{{ c.secondary_institution_name || 'Same Institution' }}</div>
                <div v-if="c.secondary_institution_code" class="font-mono text-[11px] text-text-secondary">({{ c.secondary_institution_code }})</div>
              </td>
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
                <button
                  type="button"
                  @click="openCaseDetail(c)"
                  class="px-2.5 py-1 rounded-[4px] bg-primary text-[#FFFEFA] hover:bg-primary-hover text-[11px] font-medium transition-colors"
                >
                  Inspect & Resolve
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- RESOLUTION MODAL -->
    <ModalDialog
      :open="detailModalOpen"
      :title="`Conflict Investigation: ${selectedCase?.case_reference || ''}`"
      max-width="2xl"
      @close="detailModalOpen = false"
    >
      <div v-if="selectedCase" class="space-y-4 text-[12px]">
        <!-- Comparison Summary -->
        <div class="p-3.5 bg-canvas rounded-[6px] border border-border">
          <div class="font-semibold text-text-primary text-[13px] mb-1">Conflict Summary</div>
          <p class="text-text-secondary leading-relaxed">{{ selectedCase.description }}</p>
          <div class="mt-2 text-[11px] font-mono text-text-secondary">
            Masked Identifier: <strong class="text-text-primary">{{ selectedCase.apaar_id_masked }}</strong>
          </div>
        </div>

        <!-- Resolution Decision Form -->
        <form @submit.prevent="submitResolution" class="space-y-3 pt-2">
          <div>
            <label class="block font-medium text-text-secondary mb-1">Resolution Decision *</label>
            <select
              v-model="resolutionForm.decision"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            >
              <option value="verified_valid_transfer">Verified Valid Lateral Transfer (NOC confirmed)</option>
              <option value="false_positive_cleared">False Positive Cleared (Independent identities confirmed)</option>
              <option value="institution_corrected">Mark for Institution Correction / Re-upload</option>
              <option value="record_merged_manually">Merge Historical Record</option>
              <option value="rejected_fraudulent">Reject Record as Fraudulent / Duplicate</option>
            </select>
          </div>

          <div>
            <label class="block font-medium text-text-secondary mb-1">Administrative Findings & Notes *</label>
            <textarea
              v-model="resolutionForm.notes"
              required
              rows="3"
              placeholder="State verified institutional transfer references, document IDs, or rationale..."
              class="w-full p-2.5 rounded-[6px] bg-search-bg border border-border text-[12px]"
            ></textarea>
          </div>
        </form>
      </div>

      <template #footer>
        <button
          type="button"
          @click="detailModalOpen = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px]"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="submitResolution"
          :disabled="isResolving"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle flex items-center gap-1.5 disabled:opacity-60"
        >
          <Loader2 v-if="isResolving" class="w-3.5 h-3.5 animate-spin" />
          <span>Record Decision</span>
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { duplicateApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import { Info, Loader2 } from 'lucide-vue-next';

const isLoading = ref(true);
const isResolving = ref(false);
const cases = ref<any[]>([]);

const detailModalOpen = ref(false);
const selectedCase = ref<any | null>(null);

const resolutionForm = ref({
  decision: 'verified_valid_transfer',
  notes: ''
});

async function fetchCases() {
  isLoading.value = true;
  try {
    const res = await duplicateApi.list();
    cases.value = res.data.cases || [];
  } catch (err) {
    console.error('Failed to load duplicate cases', err);
  } finally {
    isLoading.value = false;
  }
}

function openCaseDetail(c: any) {
  selectedCase.value = c;
  resolutionForm.value.notes = c.resolution_notes || '';
  detailModalOpen.value = true;
}

async function submitResolution() {
  if (!resolutionForm.value.notes.trim()) {
    alert('Please enter resolution notes');
    return;
  }

  isResolving.value = true;
  try {
    await duplicateApi.resolve(selectedCase.value.id, resolutionForm.value);
    detailModalOpen.value = false;
    alert('Case resolution recorded successfully');
    fetchCases();
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to resolve case');
  } finally {
    isResolving.value = false;
  }
}

onMounted(() => {
  fetchCases();
});
</script>
