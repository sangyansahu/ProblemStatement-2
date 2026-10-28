<template>
  <div class="space-y-6">
    <PageHeader
      title="APAAR Verification Management Queue"
      description="Identity verification tracking, simulated registry adapter testing, and manual review reconciliation."
    >
      <template #actions>
        <button
          type="button"
          @click="runBatchVerify"
          :disabled="isBatchVerifying"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5 disabled:opacity-70"
        >
          <Play v-if="!isBatchVerifying" class="w-4 h-4" />
          <Loader2 v-else class="w-4 h-4 animate-spin" />
          <span>{{ isBatchVerifying ? 'Running Batch...' : 'Run Verification Batch' }}</span>
        </button>
      </template>
    </PageHeader>

    <!-- MANDATORY SIMULATED ADAPTER NOTICE (Section 15.2) -->
    <div class="bg-caution-bg/40 border border-caution/40 rounded-[8px] p-4 text-[12px] text-caution flex items-start gap-3">
      <AlertTriangle class="w-5 h-5 shrink-0 mt-0.5 text-caution" />
      <div>
        <strong class="font-semibold block text-[13px] text-caution">
          SIMULATED VERIFICATION ADAPTER ACTIVE (EDUCATIONAL MOCK REGISTRY)
        </strong>
        <p class="mt-0.5 text-text-secondary leading-relaxed">
          Format validation is distinct from official identity verification. External AICTE/APAAR production API credentials are not yet configured; verification results shown in this queue are deterministically evaluated against synthetic demo datasets and labelled accordingly.
        </p>
      </div>
    </div>

    <!-- Status Filters -->
    <div class="flex items-center gap-2 p-1 bg-surface border border-border rounded-[8px] max-w-xl text-[12px]">
      <button
        v-for="s in ['all', 'pending', 'mismatch_detected', 'requires_manual_review', 'unable_to_verify']"
        :key="s"
        @click="filterStatus = s; fetchQueue()"
        :class="[
          'px-3 py-1.5 rounded-[5px] capitalize font-medium transition-colors',
          filterStatus === s ? 'bg-primary text-[#FFFEFA] shadow-xs' : 'text-text-secondary hover:text-text-primary'
        ]"
      >
        {{ s.replace(/_/g, ' ') }}
      </button>
    </div>

    <!-- Queue Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Student ID</th>
              <th class="py-2.5 px-4">Student Name</th>
              <th class="py-2.5 px-4">APAAR (Masked)</th>
              <th v-if="!authStore.isInstitute" class="py-2.5 px-4">Institution</th>
              <th class="py-2.5 px-4">Programme</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4">Verification Note</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="8" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading verification queue...</span>
              </td>
            </tr>
            <tr v-else-if="queue.length === 0">
              <td colspan="8" class="p-8 text-center text-success font-medium">
                ✓ No pending student records in verification queue.
              </td>
            </tr>
            <tr v-for="s in queue" :key="s.id" class="hover:bg-canvas/50 transition-colors">
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ s.student_id }}</td>
              <td class="py-3 px-4 font-medium text-text-primary">{{ s.student_name }}</td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">{{ s.apaar_id_masked }}</td>
              <td v-if="!authStore.isInstitute" class="py-3 px-4 text-text-secondary truncate max-w-[140px]">{{ s.institution_name }}</td>
              <td class="py-3 px-4 text-text-secondary truncate max-w-[140px]">{{ s.programme_name }}</td>
              <td class="py-3 px-4">
                <StatusBadge :status="s.verification_status" />
              </td>
              <td class="py-3 px-4 text-[11px] text-text-secondary truncate max-w-[220px]" :title="s.verification_notes">
                {{ s.verification_notes || 'Pending check' }}
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    @click="verifyStudent(s.id)"
                    class="text-primary hover:underline font-medium text-[11px]"
                  >
                    Verify
                  </button>
                  <button
                    v-if="authStore.isAdmin || authStore.isSuperAdmin"
                    type="button"
                    @click="openOverride(s)"
                    class="text-caution hover:underline font-medium text-[11px]"
                  >
                    Override
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MANUAL OVERRIDE MODAL -->
    <ModalDialog
      :open="overrideModalOpen"
      :title="`Manual Verification Override: ${selectedStudent?.student_name || ''}`"
      max-width="md"
      @close="overrideModalOpen = false"
    >
      <form @submit.prevent="submitOverride" class="space-y-4 text-[12px]">
        <div>
          <label class="block font-medium text-text-secondary mb-1">Decided Status</label>
          <select
            v-model="overrideForm.status"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          >
            <option value="verified">Verified (Authorized Exception / Manually Confirmed)</option>
            <option value="rejected">Rejected (Confirmed Fraudulent / Withdrawn)</option>
            <option value="requires_manual_review">Flag for Committee Review</option>
            <option value="unable_to_verify">Unable to Verify</option>
          </select>
        </div>

        <div>
          <label class="block font-medium text-text-secondary mb-1">Administrative Notes & Reason *</label>
          <textarea
            v-model="overrideForm.notes"
            required
            rows="3"
            placeholder="Document reason, document references, or physical verification findings..."
            class="w-full p-2.5 rounded-[6px] bg-search-bg border border-border text-[12px]"
          ></textarea>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="overrideModalOpen = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px]"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="submitOverride"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle"
        >
          Confirm Override
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { verificationApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import { AlertTriangle, Play, Loader2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const isLoading = ref(true);
const isBatchVerifying = ref(false);

const queue = ref<any[]>([]);
const filterStatus = ref('all');

const overrideModalOpen = ref(false);
const selectedStudent = ref<any | null>(null);
const overrideForm = ref({
  status: 'verified',
  notes: ''
});

async function fetchQueue() {
  isLoading.value = true;
  try {
    const params: any = {};
    if (filterStatus.value !== 'all') {
      params.status = filterStatus.value;
    }
    const res = await verificationApi.getQueue(params);
    queue.value = res.data.queue || [];
  } catch (err) {
    console.error('Failed to load verification queue', err);
  } finally {
    isLoading.value = false;
  }
}

async function verifyStudent(id: number) {
  try {
    const res = await verificationApi.verifySingle(id);
    alert(`Verification completed: ${res.data.verification_status.toUpperCase()}`);
    fetchQueue();
  } catch (err: any) {
    alert(err.response?.data?.message || 'Verification failed');
  }
}

async function runBatchVerify() {
  isBatchVerifying.value = true;
  try {
    const res = await verificationApi.batchVerify();
    alert(`Batch Verification Complete: ${res.data.verified_count} verified, ${res.data.flagged_count} flagged.`);
    fetchQueue();
  } catch (err: any) {
    alert('Batch run failed');
  } finally {
    isBatchVerifying.value = false;
  }
}

function openOverride(s: any) {
  selectedStudent.value = s;
  overrideForm.value.notes = '';
  overrideModalOpen.value = true;
}

async function submitOverride() {
  if (!overrideForm.value.notes.trim()) {
    alert('Please provide notes explaining the decision');
    return;
  }

  try {
    await verificationApi.manualOverride({
      student_id: selectedStudent.value.id,
      status: overrideForm.value.status,
      notes: overrideForm.value.notes
    });
    overrideModalOpen.value = false;
    alert('Manual override recorded');
    fetchQueue();
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to submit override');
  }
}

onMounted(() => {
  fetchQueue();
});
</script>
