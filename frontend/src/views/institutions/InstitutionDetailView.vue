<template>
  <div class="space-y-6">
    <!-- Back Navigation -->
    <div class="flex items-center justify-between pb-2 border-b border-border">
      <router-link
        :to="backRoute"
        class="text-[12px] text-text-secondary hover:text-primary transition-colors flex items-center gap-1.5 font-medium"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        <span>{{ backLabel }}</span>
      </router-link>

      <div class="flex items-center gap-2">
        <span class="text-[11px] font-mono text-text-secondary">
          INSTITUTION ID: <strong class="text-text-primary">{{ institution?.code || '—' }}</strong>
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="p-12 text-center text-text-secondary">
      <Loader2 class="w-6 h-6 animate-spin text-primary mx-auto mb-2" />
      <span>Loading institution profile...</span>
    </div>

    <div v-else-if="institution" class="space-y-6">
      <!-- Profile Header Card -->
      <div class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-[6px] bg-primary-soft text-primary font-bold text-[18px] flex items-center justify-center shrink-0">
              <Building2 class="w-6 h-6" />
            </div>
            <div>
              <div class="flex items-center gap-2.5">
                <h1 class="text-[22px] font-semibold text-text-primary tracking-tight">
                  {{ institution.name }}
                </h1>
                <StatusBadge :status="institution.status" />
              </div>
              <div class="flex flex-wrap items-center gap-3 text-[12px] text-text-secondary mt-1 font-mono">
                <span>Code: <strong class="text-text-primary font-medium">{{ institution.code }}</strong></span>
                <span>•</span>
                <span>{{ institution.type }}</span>
                <span>•</span>
                <span>{{ institution.district }}, {{ institution.state }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-5 border-t border-border/60 text-[12px]">
          <div>
            <span class="text-text-secondary text-[11px] block">Contact Email</span>
            <span class="font-mono text-text-primary">{{ institution.contact_email || 'Not Provided' }}</span>
          </div>
          <div>
            <span class="text-text-secondary text-[11px] block">Phone Number</span>
            <span class="font-mono text-text-primary">{{ institution.contact_phone || 'Not Provided' }}</span>
          </div>
          <div>
            <span class="text-text-secondary text-[11px] block">Principal / Director</span>
            <span class="font-medium text-text-primary">{{ institution.principal_name || 'Not Provided' }}</span>
          </div>
          <div>
            <span class="text-text-secondary text-[11px] block">Total Enrolled Students</span>
            <span class="font-mono font-semibold text-text-primary text-[14px]">{{ institution.student_count || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Tab Navigation Header (Section 3.2 & 4.2) -->
      <div class="flex items-center gap-2 border-b border-border text-[13px]">
        <button
          type="button"
          @click="activeTab = 'overview'"
          :class="[
            'px-4 py-2.5 font-medium border-b-2 transition-colors flex items-center gap-2',
            activeTab === 'overview'
              ? 'border-primary text-primary bg-primary-soft/20'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          ]"
        >
          <Layers class="w-4 h-4" />
          <span>Overview & Approved Programmes</span>
        </button>

        <button
          type="button"
          @click="activeTab = 'students'"
          :class="[
            'px-4 py-2.5 font-medium border-b-2 transition-colors flex items-center gap-2',
            activeTab === 'students'
              ? 'border-primary text-primary bg-primary-soft/20'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          ]"
        >
          <Users class="w-4 h-4" />
          <span>Enrolled Students</span>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-border text-text-primary font-semibold">
            {{ studentsTotal }}
          </span>
        </button>
      </div>

      <!-- TAB 1: OVERVIEW & PROGRAMMES -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Verification Statistics Box -->
        <div v-if="institution.verification_summary" class="bg-surface rounded-[8px] border border-border p-5 shadow-subtle">
          <h3 class="text-[14px] font-semibold text-text-primary mb-3">Institutional Verification Overview</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div class="p-3 bg-canvas rounded-[6px] border border-border">
              <span class="text-[11px] text-text-secondary uppercase tracking-wider block">Total Enrolments</span>
              <span class="text-[20px] font-mono font-semibold text-text-primary block mt-1">{{ institution.verification_summary.total }}</span>
            </div>
            <div class="p-3 bg-success-bg/30 rounded-[6px] border border-success/30">
              <span class="text-[11px] text-success uppercase tracking-wider block">Verified</span>
              <span class="text-[20px] font-mono font-semibold text-success block mt-1">{{ institution.verification_summary.verified }}</span>
            </div>
            <div class="p-3 bg-caution-bg/30 rounded-[6px] border border-caution/30">
              <span class="text-[11px] text-caution uppercase tracking-wider block">Pending</span>
              <span class="text-[20px] font-mono font-semibold text-caution block mt-1">{{ institution.verification_summary.pending }}</span>
            </div>
            <div class="p-3 bg-critical-bg/30 rounded-[6px] border border-critical/30">
              <span class="text-[11px] text-critical uppercase tracking-wider block">Discrepancy</span>
              <span class="text-[20px] font-mono font-semibold text-critical block mt-1">{{ institution.verification_summary.discrepancy }}</span>
            </div>
          </div>
        </div>

        <!-- Programmes and Approved Intakes Table -->
        <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
            <div>
              <h3 class="text-[14px] font-semibold text-text-primary">Approved Academic Programmes</h3>
              <p class="text-[11px] text-text-secondary mt-0.5">Authoritative intake capacity and enrolment monitoring</p>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                  <th class="py-2.5 px-4">Code</th>
                  <th class="py-2.5 px-4">Programme & Branch</th>
                  <th class="py-2.5 px-4">Level</th>
                  <th class="py-2.5 px-4">Approved Intake</th>
                  <th class="py-2.5 px-4">Enrolled</th>
                  <th class="py-2.5 px-4">Utilization</th>
                  <th class="py-2.5 px-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 text-[12px]">
                <tr v-if="!institution.programmes || institution.programmes.length === 0">
                  <td colspan="7" class="p-4 text-center text-text-secondary">No programmes registered yet.</td>
                </tr>
                <tr v-for="p in institution.programmes" :key="p.id" class="hover:bg-canvas/50 transition-colors">
                  <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ p.programme_code }}</td>
                  <td class="py-3 px-4">
                    <div class="font-medium text-text-primary">{{ p.programme_name }}</div>
                    <div class="text-[11px] text-text-secondary">{{ p.branch_or_department }}</div>
                  </td>
                  <td class="py-3 px-4 font-mono">{{ p.level }}</td>
                  <td class="py-3 px-4 font-mono">{{ p.approved_intake }}</td>
                  <td class="py-3 px-4 font-mono font-semibold">{{ p.actual_enrolment }}</td>
                  <td class="py-3 px-4 font-mono">{{ p.utilization_rate }}%</td>
                  <td class="py-3 px-4 text-right">
                    <StatusBadge :status="p.discrepancy_status" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB 2: ENROLLED STUDENTS (Section 3.2 & 4.2) -->
      <div v-else-if="activeTab === 'students'" class="space-y-4">
        <!-- Search and Filter Bar -->
        <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            <!-- Search -->
            <div class="relative lg:col-span-2">
              <Search class="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                v-model="studentSearch"
                @input="debouncedFetchStudents"
                type="text"
                placeholder="Search student name or ID..."
                class="w-full h-[36px] pl-9 pr-3 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-primary font-sans"
              />
            </div>

            <!-- Programme Filter -->
            <div>
              <select
                v-model="selectedProgramme"
                @change="fetchStudents(1)"
                class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
              >
                <option value="">All Programmes</option>
                <option v-for="p in institution.programmes || []" :key="p.id" :value="p.programme_name">
                  {{ p.programme_name }} ({{ p.branch_or_department }})
                </option>
              </select>
            </div>

            <!-- Enrolment Status Filter -->
            <div>
              <select
                v-model="selectedEnrolmentStatus"
                @change="fetchStudents(1)"
                class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
              >
                <option value="">All Enrolment States</option>
                <option value="Active">Active</option>
                <option value="Completed">Completed</option>
                <option value="Dropped Out">Dropped Out</option>
                <option value="Suspended">Suspended</option>
                <option value="Transferred">Transferred</option>
              </select>
            </div>

            <!-- Verification Status Filter -->
            <div>
              <select
                v-model="selectedVerificationStatus"
                @change="fetchStudents(1)"
                class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
              >
                <option value="">All Verification States</option>
                <option value="verified">Verified</option>
                <option value="pending">Pending</option>
                <option value="mismatch_detected">Mismatch Detected</option>
                <option value="requires_manual_review">Manual Review</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Student Records Table -->
        <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
                  <th class="py-2.5 px-4">Student ID</th>
                  <th class="py-2.5 px-4">Student Name</th>
                  <th class="py-2.5 px-4">Programme & Branch</th>
                  <th class="py-2.5 px-4">Academic Year</th>
                  <th class="py-2.5 px-4">APAAR Identifier</th>
                  <th class="py-2.5 px-4">Enrolment</th>
                  <th class="py-2.5 px-4">Verification</th>
                  <th class="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 text-[12px]">
                <tr v-if="isStudentsLoading">
                  <td colspan="8" class="p-8 text-center text-text-secondary">
                    <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                    <span>Loading student records for {{ institution.name }}...</span>
                  </td>
                </tr>

                <tr v-else-if="students.length === 0">
                  <td colspan="8" class="p-8 text-center text-text-secondary">
                    No student records found matching the specified filters.
                  </td>
                </tr>

                <tr v-for="s in students" :key="s.id" class="hover:bg-canvas/50 transition-colors">
                  <td class="py-3 px-4 font-mono font-medium text-text-primary">
                    {{ s.student_id }}
                  </td>
                  <td class="py-3 px-4 font-medium text-text-primary">
                    {{ s.student_name }}
                  </td>
                  <td class="py-3 px-4">
                    <div class="font-medium text-text-primary">{{ s.programme_name }}</div>
                    <div class="text-[11px] text-text-secondary">{{ s.branch_or_department }}</div>
                  </td>
                  <td class="py-3 px-4 font-mono text-text-secondary">
                    {{ s.academic_year }}
                  </td>
                  <td class="py-3 px-4 font-mono text-text-secondary">
                    {{ s.apaar_id_masked || '—' }}
                  </td>
                  <td class="py-3 px-4">
                    <StatusBadge :status="s.enrolment_status" />
                  </td>
                  <td class="py-3 px-4">
                    <StatusBadge :status="s.verification_status" />
                  </td>
                  <td class="py-3 px-4 text-right">
                    <router-link
                      :to="`/students/${s.id}`"
                      class="px-2.5 py-1 rounded-[4px] bg-canvas hover:bg-border text-primary border border-border font-medium text-[11px] inline-flex items-center gap-1 transition-colors"
                    >
                      <span>View</span>
                      <ArrowRight class="w-3 h-3" />
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Bar -->
          <div v-if="studentsPages > 1" class="px-5 py-3 border-t border-border flex items-center justify-between text-[12px] text-text-secondary">
            <span>Showing Page {{ studentsPage }} of {{ studentsPages }} ({{ studentsTotal }} total students)</span>
            <div class="flex items-center gap-1.5">
              <button
                type="button"
                :disabled="studentsPage <= 1"
                @click="fetchStudents(studentsPage - 1)"
                class="px-2.5 py-1 rounded-[4px] border border-border bg-surface hover:bg-canvas disabled:opacity-50 text-text-primary"
              >
                Previous
              </button>
              <button
                type="button"
                :disabled="studentsPage >= studentsPages"
                @click="fetchStudents(studentsPage + 1)"
                class="px-2.5 py-1 rounded-[4px] border border-border bg-surface hover:bg-canvas disabled:opacity-50 text-text-primary"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { institutionsApi, studentsApi } from '@/services/api';
import StatusBadge from '@/components/common/StatusBadge.vue';
import {
  Building2,
  ArrowLeft,
  ArrowRight,
  Loader2,
  Users,
  Layers,
  Search
} from 'lucide-vue-next';

const route = useRoute();
const authStore = useAuthStore();
const instId = Number(route.params.id);

const isLoading = ref(true);
const institution = ref<any | null>(null);
const activeTab = ref<'overview' | 'students'>('overview');

// Students Tab State
const isStudentsLoading = ref(false);
const students = ref<any[]>([]);
const studentsTotal = ref(0);
const studentsPage = ref(1);
const studentsPages = ref(1);
const studentSearch = ref('');
const selectedProgramme = ref('');
const selectedEnrolmentStatus = ref('');
const selectedVerificationStatus = ref('');

let debounceTimer: any = null;

const backRoute = computed(() => {
  if (authStore.isSuperAdmin) return '/institutions';
  return '/dashboard';
});

const backLabel = computed(() => {
  if (authStore.isSuperAdmin) return 'Return to Institution Management';
  if (authStore.isAdmin) return 'Return to Dashboard';
  return 'Return to Overview';
});

async function loadInstitution() {
  try {
    const res = !isNaN(instId) && instId > 0
      ? await institutionsApi.getById(instId)
      : await institutionsApi.getMy();
    institution.value = res.data.institution;
    if (institution.value?.id) {
      await fetchStudents(1);
    }
  } catch (err) {
    console.error('Failed to load institution details', err);
  } finally {
    isLoading.value = false;
  }
}

async function fetchStudents(page = 1) {
  if (!institution.value?.id) return;
  isStudentsLoading.value = true;
  studentsPage.value = page;

  try {
    const params: any = {
      institution_id: institution.value.id,
      page,
      per_page: 15,
    };
    if (studentSearch.value.trim()) params.search = studentSearch.value.trim();
    if (selectedProgramme.value) params.programme = selectedProgramme.value;
    if (selectedEnrolmentStatus.value) params.enrolment_status = selectedEnrolmentStatus.value;
    if (selectedVerificationStatus.value) params.verification_status = selectedVerificationStatus.value;

    const res = await studentsApi.list(params);
    students.value = res.data.students || [];
    studentsTotal.value = res.data.total || 0;
    studentsPages.value = res.data.pages || 1;
  } catch (err) {
    console.error('Failed to fetch institution students', err);
  } finally {
    isStudentsLoading.value = false;
  }
}

function debouncedFetchStudents() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchStudents(1);
  }, 300);
}

onMounted(() => {
  loadInstitution();
});
</script>
