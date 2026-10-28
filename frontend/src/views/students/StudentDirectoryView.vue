<template>
  <div class="space-y-6">
    <PageHeader
      title="Student Directory"
      description="Centralized student records registry. Student identities and APAAR identifiers are masked to ensure privacy compliance."
    >
      <template #actions>
        <button
          type="button"
          @click="exportCsv"
          :disabled="isExporting"
          class="px-3.5 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors flex items-center gap-1.5 disabled:opacity-60"
        >
          <Download class="w-3.5 h-3.5 text-text-secondary" />
          <span>{{ isExporting ? 'Exporting...' : 'Export Filtered CSV' }}</span>
        </button>
        <button
          v-if="authStore.isInstitute || authStore.isSuperAdmin"
          type="button"
          @click="openAddStudentModal = true"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <UserPlus class="w-4 h-4" />
          <span>Add Student Record</span>
        </button>
      </template>
    </PageHeader>

    <!-- Toolbar Filters -->
    <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <!-- Search Field -->
        <div class="relative lg:col-span-2">
          <Search class="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by student ID, name, or branch..."
            class="w-full h-[38px] pl-9 pr-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-sans"
          />
        </div>

        <!-- Verification Status Filter -->
        <div>
          <select
            v-model="filters.verification_status"
            @change="fetchStudents(1)"
            class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary transition-all font-sans"
          >
            <option value="">All Verification Statuses</option>
            <option value="verified">Verified</option>
            <option value="pending">Pending</option>
            <option value="mismatch_detected">Mismatch Detected</option>
            <option value="requires_manual_review">Requires Manual Review</option>
            <option value="unable_to_verify">Unable to Verify</option>
            <option value="not_submitted">Not Submitted</option>
          </select>
        </div>

        <!-- Academic Year Filter -->
        <div>
          <select
            v-model="filters.academic_year"
            @change="fetchStudents(1)"
            class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary transition-all font-sans"
          >
            <option value="">All Academic Years</option>
            <option value="2025-2026">2025-2026</option>
            <option value="2024-2025">2024-2025</option>
            <option value="2023-2024">2023-2024</option>
          </select>
        </div>

        <!-- Enrolment Status Filter -->
        <div>
          <select
            v-model="filters.enrolment_status"
            @change="fetchStudents(1)"
            class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary transition-all font-sans"
          >
            <option value="">All Enrolment States</option>
            <option value="Active">Active</option>
            <option value="Completed">Completed</option>
            <option value="Dropped Out">Dropped Out</option>
            <option value="Suspended">Suspended</option>
            <option value="Transferred">Transferred</option>
          </select>
        </div>
      </div>

      <!-- Active Filters Reset Bar -->
      <div v-if="hasActiveFilters" class="flex items-center justify-between text-[11px] pt-2 border-t border-border/60">
        <span class="text-text-secondary">Showing filtered student records</span>
        <button
          type="button"
          @click="resetFilters"
          class="text-primary hover:underline font-medium"
        >
          Reset All Filters
        </button>
      </div>
    </div>

    <!-- Student Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Student ID</th>
              <th class="py-2.5 px-4">Student Name</th>
              <th class="py-2.5 px-4">APAAR (Masked)</th>
              <th v-if="!authStore.isInstitute" class="py-2.5 px-4">Institution</th>
              <th class="py-2.5 px-4">Programme & Branch</th>
              <th class="py-2.5 px-4">Year</th>
              <th class="py-2.5 px-4">Enrolment</th>
              <th class="py-2.5 px-4">Verification</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td :colspan="authStore.isInstitute ? 8 : 9" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading student records from database...</span>
              </td>
            </tr>
            <tr v-else-if="students.length === 0">
              <td :colspan="authStore.isInstitute ? 8 : 9" class="p-8 text-center text-text-secondary">
                No student records found matching current criteria.
              </td>
            </tr>
            <tr
              v-for="s in students"
              :key="s.id"
              class="hover:bg-canvas/50 transition-colors"
            >
              <td class="py-3 px-4 font-mono font-medium text-text-primary">
                {{ s.student_id }}
              </td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary">{{ s.student_name }}</div>
                <div v-if="s.is_duplicate_flagged" class="text-[10px] text-bronze font-mono font-semibold flex items-center gap-1 mt-0.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-bronze"></span>
                  <span>DUPLICATE FLAGGED</span>
                </div>
              </td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">
                {{ s.apaar_id_masked }}
              </td>
              <td v-if="!authStore.isInstitute" class="py-3 px-4 text-text-secondary truncate max-w-[150px]">
                {{ s.institution_name }}
              </td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary truncate max-w-[180px]">{{ s.programme_name }}</div>
                <div class="text-[11px] text-text-secondary truncate max-w-[180px]">{{ s.branch_or_department }}</div>
              </td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">{{ s.academic_year }}</td>
              <td class="py-3 px-4">
                <span class="text-[11px] font-medium text-text-primary">{{ s.enrolment_status }}</span>
              </td>
              <td class="py-3 px-4">
                <StatusBadge :status="s.verification_status" />
              </td>
              <td class="py-3 px-4 text-right">
                <router-link
                  :to="`/students/${s.id}`"
                  class="inline-flex items-center gap-1 text-[11px] text-primary hover:underline font-medium"
                >
                  <span>View Details</span>
                  <ChevronRight class="w-3.5 h-3.5" />
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Bar -->
      <div class="px-4 py-3 border-t border-border bg-[#FBFBFA] flex items-center justify-between text-[12px] text-text-secondary font-mono">
        <div>
          Total {{ totalCount }} records • Page {{ currentPage }} of {{ totalPages || 1 }}
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="currentPage <= 1"
            @click="fetchStudents(currentPage - 1)"
            class="px-2.5 py-1 rounded-[4px] bg-surface hover:bg-canvas border border-border disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <button
            type="button"
            :disabled="currentPage >= totalPages"
            @click="fetchStudents(currentPage + 1)"
            class="px-2.5 py-1 rounded-[4px] bg-surface hover:bg-canvas border border-border disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- ADD STUDENT MODAL DIALOG -->
    <ModalDialog
      :open="openAddStudentModal"
      title="Add New Student Enrolment Record"
      max-width="lg"
      @close="openAddStudentModal = false"
    >
      <form @submit.prevent="createStudent" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Student Roll / ID *</label>
            <input
              v-model="newStudent.student_id"
              required
              placeholder="e.g. STU-2025-055"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
            />
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Student Full Name *</label>
            <input
              v-model="newStudent.student_name"
              required
              placeholder="Full name as per official ID"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">APAAR Identifier (12 Digits)</label>
            <input
              v-model="newStudent.apaar_id"
              maxlength="12"
              placeholder="e.g. 123456789012"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
            />
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Programme Name *</label>
            <input
              v-model="newStudent.programme_name"
              required
              placeholder="e.g. Bachelor of Technology"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Branch / Department *</label>
            <input
              v-model="newStudent.branch_or_department"
              required
              placeholder="e.g. Computer Science & Engineering"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            />
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Academic Year</label>
            <select
              v-model="newStudent.academic_year"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            >
              <option value="2025-2026">2025-2026</option>
              <option value="2024-2025">2024-2025</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Enrolment Status</label>
            <select
              v-model="newStudent.enrolment_status"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            >
              <option value="Active">Active</option>
              <option value="Transferred">Transferred</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Admission Category</label>
            <select
              v-model="newStudent.admission_category"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            >
              <option value="General">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="EWS">EWS</option>
            </select>
          </div>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="openAddStudentModal = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px] font-medium"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="createStudent"
          :disabled="isSubmitting"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle flex items-center gap-1.5"
        >
          <Loader2 v-if="isSubmitting" class="w-3.5 h-3.5 animate-spin" />
          <span>Save Record</span>
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { studentsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import {
  Download,
  UserPlus,
  Search,
  ChevronRight,
  Loader2
} from 'lucide-vue-next';

const route = useRoute();
const authStore = useAuthStore();

const isLoading = ref(true);
const isExporting = ref(false);
const isSubmitting = ref(false);
const openAddStudentModal = ref(false);

const students = ref<any[]>([]);
const totalCount = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);

const filters = ref({
  search: (route.query.search as string) || '',
  verification_status: '',
  academic_year: '',
  enrolment_status: '',
});

const newStudent = ref({
  student_id: '',
  student_name: '',
  apaar_id: '',
  programme_name: 'Bachelor of Technology',
  branch_or_department: 'Computer Science & Engineering',
  academic_year: '2025-2026',
  enrolment_status: 'Active',
  admission_category: 'General'
});

const hasActiveFilters = computed(() => {
  return !!filters.value.search || !!filters.value.verification_status || !!filters.value.academic_year || !!filters.value.enrolment_status;
});

let debounceTimer: any = null;
function debouncedSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchStudents(1);
  }, 300);
}

function resetFilters() {
  filters.value = {
    search: '',
    verification_status: '',
    academic_year: '',
    enrolment_status: '',
  };
  fetchStudents(1);
}

async function fetchStudents(page = 1) {
  isLoading.value = true;
  currentPage.value = page;
  try {
    const res = await studentsApi.list({
      page,
      per_page: 15,
      search: filters.value.search,
      verification_status: filters.value.verification_status,
      academic_year: filters.value.academic_year,
      enrolment_status: filters.value.enrolment_status,
    });
    students.value = res.data.students || [];
    totalCount.value = res.data.total || 0;
    totalPages.value = res.data.pages || 1;
  } catch (err) {
    console.error('Failed to load students', err);
  } finally {
    isLoading.value = false;
  }
}

async function createStudent() {
  isSubmitting.value = true;
  try {
    await studentsApi.create(newStudent.value);
    openAddStudentModal.value = false;
    alert('Student record created successfully');
    fetchStudents(1);
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to create student record');
  } finally {
    isSubmitting.value = false;
  }
}

async function exportCsv() {
  isExporting.value = true;
  try {
    const res = await studentsApi.exportCsv();
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `students_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    alert('Failed to export students CSV');
  } finally {
    isExporting.value = false;
  }
}

onMounted(() => {
  fetchStudents(1);
});
</script>
