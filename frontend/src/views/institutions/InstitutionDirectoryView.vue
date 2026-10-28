<template>
  <div class="space-y-6">
    <PageHeader
      title="Institution Directory"
      description="Registered higher education institutions, universities, and polytechnics under AICTE purview."
    >
      <template #actions>
        <button
          v-if="authStore.isSuperAdmin"
          type="button"
          @click="openAddModal = true"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <Plus class="w-4 h-4" />
          <span>Register New Institution</span>
        </button>
      </template>
    </PageHeader>

    <!-- Filters Toolbar -->
    <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="relative">
        <Search class="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          v-model="search"
          @input="fetchInstitutions(1)"
          type="text"
          placeholder="Search by code, name, or city..."
          class="w-full h-[38px] pl-9 pr-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
        />
      </div>

      <div>
        <select
          v-model="stateFilter"
          @change="fetchInstitutions(1)"
          class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
        >
          <option value="">All States</option>
          <option value="Delhi">Delhi</option>
          <option value="Maharashtra">Maharashtra</option>
          <option value="Karnataka">Karnataka</option>
          <option value="Tamil Nadu">Tamil Nadu</option>
        </select>
      </div>

      <div>
        <select
          v-model="statusFilter"
          @change="fetchInstitutions(1)"
          class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Code</th>
              <th class="py-2.5 px-4">Institution Name</th>
              <th class="py-2.5 px-4">Type</th>
              <th class="py-2.5 px-4">Location</th>
              <th class="py-2.5 px-4">Students</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="7" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading institutions...</span>
              </td>
            </tr>
            <tr v-else-if="institutions.length === 0">
              <td colspan="7" class="p-8 text-center text-text-secondary">
                No institutions found matching criteria.
              </td>
            </tr>
            <tr
              v-for="inst in institutions"
              :key="inst.id"
              class="hover:bg-canvas/50 transition-colors"
            >
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ inst.code }}</td>
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary">{{ inst.name }}</div>
                <div class="text-[11px] text-text-secondary mt-0.5">{{ inst.contact_email || 'No email' }}</div>
              </td>
              <td class="py-3 px-4 text-text-secondary">{{ inst.type }}</td>
              <td class="py-3 px-4 text-text-secondary">{{ inst.district }}, {{ inst.state }}</td>
              <td class="py-3 px-4 font-mono font-medium text-text-primary">{{ inst.student_count || 0 }}</td>
              <td class="py-3 px-4">
                <StatusBadge :status="inst.status" />
              </td>
              <td class="py-3 px-4 text-right">
                <router-link
                  :to="`/institutions/${inst.id}`"
                  class="text-[11px] text-primary hover:underline font-medium inline-flex items-center gap-1"
                >
                  <span>Profile</span>
                  <ChevronRight class="w-3.5 h-3.5" />
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- REGISTER INSTITUTION MODAL -->
    <ModalDialog
      :open="openAddModal"
      title="Register New Institution"
      max-width="lg"
      @close="openAddModal = false"
    >
      <form @submit.prevent="createInstitution" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">AICTE Code *</label>
            <input
              v-model="newInst.code"
              required
              placeholder="e.g. AICTE-1-009999"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
            />
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">Institution Type</label>
            <select
              v-model="newInst.type"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            >
              <option value="Affiliated Engineering College">Affiliated Engineering College</option>
              <option value="State University">State University</option>
              <option value="Deemed University">Deemed University</option>
              <option value="Polytechnic">Polytechnic</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-[11px] font-medium text-text-secondary mb-1">Institution Name *</label>
          <input
            v-model="newInst.name"
            required
            placeholder="Official full institution name"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">State *</label>
            <input
              v-model="newInst.state"
              required
              placeholder="e.g. Maharashtra"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            />
          </div>
          <div>
            <label class="block text-[11px] font-medium text-text-secondary mb-1">District *</label>
            <input
              v-model="newInst.district"
              required
              placeholder="e.g. Pune"
              class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
            />
          </div>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="openAddModal = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px] font-medium"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="createInstitution"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle"
        >
          Register Institution
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { institutionsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import {
  Search,
  Plus,
  ChevronRight,
  Loader2
} from 'lucide-vue-next';

const authStore = useAuthStore();
const isLoading = ref(true);
const openAddModal = ref(false);

const institutions = ref<any[]>([]);
const search = ref('');
const stateFilter = ref('');
const statusFilter = ref('');

const newInst = ref({
  code: '',
  name: '',
  type: 'Affiliated Engineering College',
  state: '',
  district: ''
});

async function fetchInstitutions(page = 1) {
  isLoading.value = true;
  try {
    const res = await institutionsApi.list({
      page,
      search: search.value,
      state: stateFilter.value,
      status: statusFilter.value,
    });
    institutions.value = res.data.institutions || [];
  } catch (err) {
    console.error('Failed to load institutions', err);
  } finally {
    isLoading.value = false;
  }
}

async function createInstitution() {
  try {
    await institutionsApi.create(newInst.value);
    openAddModal.value = false;
    alert('Institution registered successfully');
    fetchInstitutions(1);
  } catch (err: any) {
    alert(err.response?.data?.error || 'Registration failed');
  }
}

onMounted(() => {
  fetchInstitutions(1);
});
</script>
