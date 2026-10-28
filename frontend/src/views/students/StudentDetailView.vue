<template>
  <div class="space-y-6">
    <!-- Back to directory link & Actions -->
    <div class="flex items-center justify-between pb-2 border-b border-border">
      <router-link to="/students" class="text-[12px] text-text-secondary hover:text-primary transition-colors flex items-center gap-1">
        <ArrowLeft class="w-3.5 h-3.5" />
        <span>Return to Student Directory</span>
      </router-link>

      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="verifyNow"
          :disabled="isVerifying"
          class="px-3 py-1.5 rounded-[6px] bg-surface hover:bg-canvas text-primary border border-primary/30 text-[12px] font-medium transition-colors flex items-center gap-1.5"
        >
          <Play class="w-3.5 h-3.5" />
          <span>{{ isVerifying ? 'Verifying...' : 'Run APAAR Check' }}</span>
        </button>
        <button
          type="button"
          @click="openEditModal = true"
          class="px-3.5 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <Edit2 class="w-3.5 h-3.5" />
          <span>Correct / Edit Record</span>
        </button>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="p-12 text-center text-text-secondary">
      <Loader2 class="w-6 h-6 animate-spin text-primary mx-auto mb-2" />
      <span>Loading student record...</span>
    </div>

    <div v-else-if="student" class="space-y-6">
      <!-- Top Profile Overview Card -->
      <div class="bg-surface rounded-[8px] border border-border p-5 sm:p-6 shadow-subtle">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center gap-3.5">
            <div class="w-12 h-12 rounded-full bg-primary-soft text-primary font-bold text-[16px] flex items-center justify-center font-mono">
              {{ studentInitials }}
            </div>
            <div>
              <div class="flex items-center gap-2.5">
                <h1 class="text-[20px] font-semibold text-text-primary tracking-tight">
                  {{ student.student_name }}
                </h1>
                <StatusBadge :status="student.verification_status" />
              </div>
              <div class="flex flex-wrap items-center gap-3 text-[12px] text-text-secondary mt-1 font-mono">
                <span>ID: <strong class="text-text-primary font-medium">{{ student.student_id }}</strong></span>
                <span>•</span>
                <span>APAAR: <strong class="text-text-primary font-medium">{{ student.apaar_id_masked }}</strong></span>
                <span>•</span>
                <span>{{ student.academic_year }}</span>
              </div>
            </div>
          </div>

          <div v-if="student.is_duplicate_flagged" class="px-3 py-1.5 rounded-[6px] bg-caution-bg border border-caution/30 text-caution text-[11px] font-mono flex items-center gap-1.5">
            <AlertTriangle class="w-4 h-4 shrink-0" />
            <span>Cross-Institution Conflict Flagged</span>
          </div>
        </div>
      </div>

      <!-- Information Sections Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Section 1: Institution & Academic Details -->
        <div class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle space-y-3">
          <h3 class="text-[14px] font-semibold text-text-primary border-b border-border/60 pb-2">
            Academic & Programme Registration
          </h3>
          <div class="grid grid-cols-2 gap-y-3 text-[12px]">
            <div>
              <span class="text-text-secondary text-[11px] block">Institution</span>
              <span class="font-medium text-text-primary">{{ student.institution_name }}</span>
              <span class="text-[11px] font-mono text-text-secondary block">({{ student.institution_code }})</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Programme Name</span>
              <span class="font-medium text-text-primary">{{ student.programme_name }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Branch / Department</span>
              <span class="font-medium text-text-primary">{{ student.branch_or_department }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Academic Year</span>
              <span class="font-mono text-text-primary">{{ student.academic_year }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Admission Date</span>
              <span class="font-mono text-text-primary">{{ student.admission_date || 'N/A' }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Enrolment Status</span>
              <span class="font-medium text-text-primary">{{ student.enrolment_status }}</span>
            </div>
          </div>
        </div>

        <!-- Section 2: APAAR & Verification Details -->
        <div class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle space-y-3">
          <h3 class="text-[14px] font-semibold text-text-primary border-b border-border/60 pb-2">
            Identity & APAAR Verification
          </h3>
          <div class="grid grid-cols-2 gap-y-3 text-[12px]">
            <div>
              <span class="text-text-secondary text-[11px] block">Masked Identifier</span>
              <span class="font-mono text-text-primary font-semibold">{{ student.apaar_id_masked }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Verification Status</span>
              <StatusBadge :status="student.verification_status" class="mt-0.5" />
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Verification Source</span>
              <span class="font-mono text-text-primary">{{ student.verification_source }}</span>
            </div>
            <div>
              <span class="text-text-secondary text-[11px] block">Verified Timestamp</span>
              <span class="font-mono text-text-secondary text-[11px]">{{ student.verified_at ? formatDate(student.verified_at) : 'Not Yet' }}</span>
            </div>
            <div class="col-span-2">
              <span class="text-text-secondary text-[11px] block">Verification Notes</span>
              <p class="text-[12px] text-text-secondary bg-canvas/60 p-2.5 rounded-[4px] border border-border mt-1">
                {{ student.verification_notes || 'No verification notes registered.' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 3: Related Duplicate / Conflict Cases (if any) -->
      <div v-if="student.related_duplicate_cases && student.related_duplicate_cases.length > 0" class="bg-surface rounded-[8px] border border-caution/40 p-5 shadow-subtle">
        <h3 class="text-[14px] font-semibold text-caution mb-2 flex items-center gap-1.5">
          <AlertTriangle class="w-4 h-4" />
          <span>Active Duplicate & Conflict Review Cases</span>
        </h3>
        <div class="space-y-2">
          <div
            v-for="c in student.related_duplicate_cases"
            :key="c.id"
            class="p-3 rounded-[6px] bg-canvas border border-border flex items-center justify-between text-[12px]"
          >
            <div>
              <div class="font-mono font-semibold text-text-primary">{{ c.case_reference }} ({{ c.issue_type }})</div>
              <div class="text-[11px] text-text-secondary mt-0.5">{{ c.description }}</div>
            </div>
            <router-link to="/duplicate-review" class="text-primary hover:underline font-medium text-[11px] shrink-0">
              Open Conflict Panel →
            </router-link>
          </div>
        </div>
      </div>

      <!-- Section 4: Record Change History & Audit Timeline -->
      <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
        <div class="px-5 py-3.5 border-b border-border">
          <h3 class="text-[14px] font-semibold text-text-primary">Record Modification Audit History</h3>
          <p class="text-[11px] text-text-secondary mt-0.5">Granular chronological trail of all edits and manual overrides</p>
        </div>

        <div class="p-5">
          <div v-if="!student.change_history || student.change_history.length === 0" class="text-text-secondary text-[12px] text-center p-4">
            No manual edits or status modifications recorded for this student.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="ch in student.change_history"
              :key="ch.id"
              class="flex items-start gap-3 text-[12px] p-2.5 rounded-[4px] bg-canvas border border-border/60"
            >
              <div class="w-2 h-2 rounded-full bg-primary shrink-0 mt-1.5"></div>
              <div class="flex-1">
                <div class="flex items-center justify-between font-mono text-[11px]">
                  <span class="font-semibold text-text-primary">{{ ch.change_type }} • {{ ch.field_name || 'all' }}</span>
                  <span class="text-text-secondary">{{ formatDate(ch.timestamp) }}</span>
                </div>
                <div class="text-[11px] text-text-secondary mt-0.5">
                  By <strong class="text-text-primary">{{ ch.changed_by_name }}</strong>
                </div>
                <div v-if="ch.reason" class="text-[11px] text-text-secondary mt-1 italic">
                  "{{ ch.reason }}"
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- EDIT RECORD MODAL -->
    <ModalDialog
      :open="openEditModal"
      title="Correct Student Record"
      max-width="lg"
      @close="openEditModal = false"
    >
      <form @submit.prevent="submitCorrection" class="space-y-4">
        <div>
          <label class="block text-[11px] font-medium text-text-secondary mb-1">Student Full Name</label>
          <input
            v-model="editForm.student_name"
            required
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          />
        </div>

        <div>
          <label class="block text-[11px] font-medium text-text-secondary mb-1">APAAR Identifier (12 Digits)</label>
          <input
            v-model="editForm.apaar_id"
            placeholder="Enter 12 digits to update APAAR ID"
            maxlength="12"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
          />
        </div>

        <div>
          <label class="block text-[11px] font-medium text-text-secondary mb-1">Enrolment Status</label>
          <select
            v-model="editForm.enrolment_status"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          >
            <option value="Active">Active</option>
            <option value="Completed">Completed</option>
            <option value="Dropped Out">Dropped Out</option>
            <option value="Suspended">Suspended</option>
            <option value="Transferred">Transferred</option>
          </select>
        </div>

        <div>
          <label class="block text-[11px] font-medium text-text-secondary mb-1">Reason for Edit / Correction *</label>
          <textarea
            v-model="editForm.reason"
            required
            rows="2"
            placeholder="State the institutional justification for updating this student record..."
            class="w-full p-2.5 rounded-[6px] bg-search-bg border border-border text-[12px]"
          ></textarea>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="openEditModal = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px] font-medium"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="submitCorrection"
          :disabled="isSubmitting"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle flex items-center gap-1.5"
        >
          <Loader2 v-if="isSubmitting" class="w-3.5 h-3.5 animate-spin" />
          <span>Save Changes</span>
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { studentsApi, verificationApi } from '@/services/api';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import {
  ArrowLeft,
  Play,
  Edit2,
  AlertTriangle,
  Loader2
} from 'lucide-vue-next';

const route = useRoute();
const studentId = Number(route.params.id);

const isLoading = ref(true);
const isVerifying = ref(false);
const isSubmitting = ref(false);
const openEditModal = ref(false);
const student = ref<any | null>(null);

const editForm = ref({
  student_name: '',
  apaar_id: '',
  enrolment_status: 'Active',
  reason: ''
});

const studentInitials = computed(() => {
  if (!student.value?.student_name) return 'S';
  return student.value.student_name.split(' ').map((n: string) => n[0]).slice(0, 2).join('').toUpperCase();
});

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

async function loadStudent() {
  isLoading.value = true;
  try {
    const res = await studentsApi.getById(studentId);
    student.value = res.data.student;
    editForm.value.student_name = student.value.student_name;
    editForm.value.enrolment_status = student.value.enrolment_status;
  } catch (err) {
    console.error('Failed to load student details', err);
  } finally {
    isLoading.value = false;
  }
}

async function verifyNow() {
  isVerifying.value = true;
  try {
    const res = await verificationApi.verifySingle(studentId);
    alert(`Verification check complete: ${res.data.verification_status.toUpperCase()}`);
    loadStudent();
  } catch (err: any) {
    alert(err.response?.data?.message || 'Verification failed');
  } finally {
    isVerifying.value = false;
  }
}

async function submitCorrection() {
  if (!editForm.value.reason.trim()) {
    alert('Please provide a reason for the record modification');
    return;
  }

  isSubmitting.value = true;
  try {
    await studentsApi.update(studentId, editForm.value);
    openEditModal.value = false;
    alert('Student record updated successfully');
    loadStudent();
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to update record');
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  loadStudent();
});
</script>
