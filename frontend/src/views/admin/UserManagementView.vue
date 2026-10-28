<template>
  <div class="space-y-6">
    <PageHeader
      title="User Account & Role Management"
      description="Administrative user provisioning, role assignments (Institute, Admin, Super Admin), and account activation state control."
    >
      <template #actions>
        <button
          type="button"
          @click="openAddModal = true"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <UserPlus class="w-4 h-4" />
          <span>Provision New User Account</span>
        </button>
      </template>
    </PageHeader>

    <!-- User Table -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4">Full Name</th>
              <th class="py-2.5 px-4">Username / Identifier</th>
              <th class="py-2.5 px-4">Role</th>
              <th class="py-2.5 px-4">Associated Institution</th>
              <th class="py-2.5 px-4">Last Login</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="7" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Loading user directory...</span>
              </td>
            </tr>
            <tr v-for="u in users" :key="u.id" class="hover:bg-canvas/50 transition-colors">
              <td class="py-3 px-4 font-medium text-text-primary">
                {{ u.full_name }}
              </td>
              <td class="py-3 px-4 font-mono text-text-secondary">
                {{ u.username }}
              </td>
              <td class="py-3 px-4">
                <span
                  :class="[
                    'text-[10px] font-mono px-2 py-0.5 rounded-sm uppercase font-semibold border',
                    u.role === 'super_admin' ? 'bg-critical-bg text-critical border-critical/30' :
                    u.role === 'admin' ? 'bg-primary-soft text-primary border-primary/30' :
                    'bg-canvas text-text-secondary border-border'
                  ]"
                >
                  {{ u.role.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4 text-text-secondary truncate max-w-[200px]">
                {{ u.institution_name || 'All Institutions (Central)' }}
              </td>
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary">
                {{ u.last_login ? formatDate(u.last_login) : 'Never' }}
              </td>
              <td class="py-3 px-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm text-[11px] font-mono',
                    u.is_active ? 'bg-success-bg text-success' : 'bg-critical-bg text-critical'
                  ]"
                >
                  <span :class="['w-1.5 h-1.5 rounded-full', u.is_active ? 'bg-success' : 'bg-critical']"></span>
                  <span>{{ u.is_active ? 'Active' : 'Inactive' }}</span>
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button
                  type="button"
                  @click="toggleStatus(u)"
                  class="text-[11px] text-text-secondary hover:text-text-primary underline font-medium"
                >
                  {{ u.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ADD USER MODAL -->
    <ModalDialog
      :open="openAddModal"
      title="Provision User Account"
      max-width="md"
      @close="openAddModal = false"
    >
      <form @submit.prevent="createUser" class="space-y-3.5 text-[12px]">
        <div>
          <label class="block font-medium text-text-secondary mb-1">Full Name *</label>
          <input
            v-model="newUser.full_name"
            required
            placeholder="Official full name"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          />
        </div>

        <div>
          <label class="block font-medium text-text-secondary mb-1">Account Identifier (Username) *</label>
          <input
            v-model="newUser.username"
            required
            placeholder="e.g. jdoe_admin"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
          />
        </div>

        <div>
          <label class="block font-medium text-text-secondary mb-1">Email Address *</label>
          <input
            v-model="newUser.email"
            type="email"
            required
            placeholder="e.g. official@aicte-india.org"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          />
        </div>

        <div>
          <label class="block font-medium text-text-secondary mb-1">System Role *</label>
          <select
            v-model="newUser.role"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px]"
          >
            <option value="institute">Institute (Limited to specific institution)</option>
            <option value="admin">Admin (Read-only cross-institution review)</option>
            <option value="super_admin">Super Admin (Full platform management)</option>
          </select>
        </div>

        <div v-if="newUser.role === 'institute'">
          <label class="block font-medium text-text-secondary mb-1">Linked Institution ID *</label>
          <input
            v-model.number="newUser.institution_id"
            type="number"
            required
            placeholder="e.g. 1"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
          />
        </div>

        <div>
          <label class="block font-medium text-text-secondary mb-1">Initial Password *</label>
          <input
            v-model="newUser.password"
            type="password"
            required
            placeholder="Minimum 8 characters"
            class="w-full h-[36px] px-3 rounded-[6px] bg-search-bg border border-border text-[12px] font-mono"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          @click="openAddModal = false"
          class="px-3.5 py-1.5 rounded-[6px] bg-surface hover:bg-canvas border border-border text-[12px]"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="createUser"
          class="px-4 py-1.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium shadow-subtle"
        >
          Provision Account
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { usersApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import { UserPlus, Loader2 } from 'lucide-vue-next';

const isLoading = ref(true);
const users = ref<any[]>([]);
const openAddModal = ref(false);

const newUser = ref({
  full_name: '',
  username: '',
  email: '',
  role: 'institute',
  institution_id: 1,
  password: ''
});

function formatDate(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
}

async function fetchUsers() {
  isLoading.value = true;
  try {
    const res = await usersApi.list();
    users.value = res.data.users || [];
  } catch (err) {
    console.error('Failed to load users', err);
  } finally {
    isLoading.value = false;
  }
}

async function createUser() {
  try {
    await usersApi.create(newUser.value);
    openAddModal.value = false;
    alert('User account provisioned successfully');
    fetchUsers();
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to create user');
  }
}

async function toggleStatus(user: any) {
  try {
    await usersApi.toggleStatus(user.id, !user.is_active);
    user.is_active = !user.is_active;
  } catch (err: any) {
    alert(err.response?.data?.error || 'Failed to toggle status');
  }
}

onMounted(() => {
  fetchUsers();
});
</script>
