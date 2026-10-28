<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <PageHeader
        title="Audit Logs & Governance Trails"
        description="Immutable system-wide ledger capturing student mutations, enrolment changes, verification actions, and administrative operations."
      />
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-mono text-text-secondary bg-surface border border-border px-3 py-1.5 rounded-[6px] shadow-subtle">
          AUDIT RETENTION: <strong class="text-text-primary">5 YEARS</strong>
        </span>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="bg-surface rounded-[8px] border border-border p-4 shadow-subtle space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <!-- Search Field -->
        <div class="relative lg:col-span-2">
          <Search class="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            v-model="searchQuery"
            @input="debouncedFetchLogs"
            type="text"
            placeholder="Search by user, action, summary, or record ID..."
            class="w-full h-[36px] pl-9 pr-3 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:border-primary font-sans"
          />
        </div>

        <!-- Target Entity Filter -->
        <div>
          <select
            v-model="selectedTarget"
            @change="fetchLogs(1)"
            class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
          >
            <option value="">All Entities</option>
            <option value="Student">Student</option>
            <option value="Institution">Institution</option>
            <option value="UploadBatch">Upload Batch</option>
            <option value="DuplicateCase">Duplicate Case</option>
            <option value="User">User Account</option>
            <option value="SystemSettings">System Settings</option>
          </select>
        </div>

        <!-- Action Filter -->
        <div>
          <select
            v-model="selectedAction"
            @change="fetchLogs(1)"
            class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
          >
            <option value="">All Actions</option>
            <option v-for="act in availableActions" :key="act" :value="act">
              {{ formatActionLabel(act) }}
            </option>
          </select>
        </div>

        <!-- Role Filter -->
        <div>
          <select
            v-model="selectedRole"
            @change="fetchLogs(1)"
            class="w-full h-[36px] px-2.5 rounded-[6px] bg-search-bg border border-border text-[12px] text-text-primary focus:outline-none focus:border-primary"
          >
            <option value="">All Roles</option>
            <option value="super_admin">Super Admin</option>
            <option value="admin">Admin</option>
            <option value="institute">Institute</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Audit Logs Compact Table (Section 3.3) -->
    <div class="bg-surface rounded-[8px] border border-border shadow-subtle overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-table-header border-b border-border text-[11px] font-semibold text-text-secondary uppercase tracking-wider">
              <th class="py-2.5 px-4 w-[160px]">Date & Time</th>
              <th class="py-2.5 px-4 w-[190px]">User</th>
              <th class="py-2.5 px-4 w-[180px]">Action</th>
              <th class="py-2.5 px-4 w-[150px]">Affected Record</th>
              <th class="py-2.5 px-4">Change Summary</th>
              <th class="py-2.5 px-4 text-right w-[80px]">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-[12px]">
            <tr v-if="isLoading">
              <td colspan="6" class="p-8 text-center text-text-secondary">
                <Loader2 class="w-5 h-5 text-primary animate-spin mx-auto mb-2" />
                <span>Retrieving verified audit ledger...</span>
              </td>
            </tr>

            <tr v-else-if="logs.length === 0">
              <td colspan="6" class="p-8 text-center text-text-secondary">
                No audit events found matching the specified query criteria.
              </td>
            </tr>

            <tr
              v-for="log in logs"
              :key="log.id"
              class="hover:bg-canvas/50 transition-colors"
            >
              <!-- 1. Date & Time -->
              <td class="py-3 px-4 font-mono text-[11px] text-text-secondary whitespace-nowrap">
                {{ formatDate(log.created_at) }}
              </td>

              <!-- 2. User -->
              <td class="py-3 px-4">
                <div class="font-medium text-text-primary truncate max-w-[170px]" :title="log.actor_name">
                  {{ log.actor_name }}
                </div>
                <div class="text-[10px] font-mono text-text-secondary uppercase mt-0.5">
                  {{ formatRole(log.actor_role) }}
                </div>
              </td>

              <!-- 3. Action -->
              <td class="py-3 px-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[11px] font-medium border',
                    getActionBadgeClass(log.action, log.outcome)
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      log.outcome === 'FAILED' ? 'bg-critical' : 'bg-primary'
                    ]"
                  ></span>
                  <span>{{ formatActionLabel(log.action) }}</span>
                </span>
              </td>

              <!-- 4. Affected Record -->
              <td class="py-3 px-4 font-mono text-[11px] text-text-primary whitespace-nowrap">
                <span class="text-text-secondary">{{ log.target_type }}</span>
                <span v-if="log.target_id" class="font-semibold block text-primary">
                  {{ log.target_id }}
                </span>
              </td>

              <!-- 5. Change Summary -->
              <td class="py-3 px-4 text-text-primary leading-relaxed">
                <div class="truncate max-w-[420px]" :title="log.summary">
                  {{ log.summary }}
                </div>
              </td>

              <!-- Actions -->
              <td class="py-3 px-4 text-right whitespace-nowrap">
                <button
                  type="button"
                  @click="openLogDetails(log)"
                  class="px-2.5 py-1 rounded-[4px] bg-canvas hover:bg-border text-primary border border-border font-medium text-[11px] transition-colors inline-flex items-center gap-1"
                >
                  <span>Inspect</span>
                  <ExternalLink class="w-3 h-3" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-5 py-3 border-t border-border flex items-center justify-between text-[12px] text-text-secondary">
        <span>Showing Page {{ currentPage }} of {{ totalPages }} ({{ totalLogs }} total events)</span>
        <div class="flex items-center gap-1.5">
          <button
            type="button"
            :disabled="currentPage <= 1"
            @click="fetchLogs(currentPage - 1)"
            class="px-2.5 py-1 rounded-[4px] border border-border bg-surface hover:bg-canvas disabled:opacity-50 text-text-primary"
          >
            Previous
          </button>
          <button
            type="button"
            :disabled="currentPage >= totalPages"
            @click="fetchLogs(currentPage + 1)"
            class="px-2.5 py-1 rounded-[4px] border border-border bg-surface hover:bg-canvas disabled:opacity-50 text-text-primary"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Audit Event Detail Dialog (Section 3.3) -->
    <ModalDialog
      v-if="selectedLog"
      :open="!!selectedLog"
      title="Audit Event Details"
      maxWidth="lg"
      @close="selectedLog = null"
    >
      <div class="space-y-4 text-[13px]">
        <!-- Overview Grid -->
        <div class="grid grid-cols-2 gap-4 p-4 rounded-[6px] bg-canvas border border-border">
          <div>
            <span class="text-[11px] text-text-secondary block">Action Type</span>
            <span class="font-mono font-medium text-text-primary text-[12px]">{{ selectedLog.action }}</span>
          </div>
          <div>
            <span class="text-[11px] text-text-secondary block">Outcome</span>
            <span
              :class="[
                'font-mono font-semibold text-[11px] px-1.5 py-0.5 rounded-sm inline-block',
                selectedLog.outcome === 'FAILED' ? 'bg-critical-bg text-critical' : 'bg-success-bg text-success'
              ]"
            >
              {{ selectedLog.outcome }}
            </span>
          </div>
          <div>
            <span class="text-[11px] text-text-secondary block">Actor</span>
            <span class="font-medium text-text-primary">{{ selectedLog.actor_name }} ({{ selectedLog.actor_role }})</span>
          </div>
          <div>
            <span class="text-[11px] text-text-secondary block">Timestamp & Origin</span>
            <span class="font-mono text-[11px] text-text-secondary">
              {{ formatDate(selectedLog.created_at) }} • {{ selectedLog.ip_address }}
            </span>
          </div>
        </div>

        <!-- Summary -->
        <div>
          <label class="block text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-1">
            Change Summary
          </label>
          <p class="p-3 rounded-[6px] bg-surface border border-border text-text-primary text-[12px] leading-relaxed">
            {{ selectedLog.summary }}
          </p>
        </div>

        <!-- Target Information -->
        <div class="grid grid-cols-2 gap-3 p-3 rounded-[6px] bg-surface border border-border">
          <div>
            <span class="text-[11px] text-text-secondary block">Target Entity Type</span>
            <span class="font-mono text-text-primary">{{ selectedLog.target_type }}</span>
          </div>
          <div>
            <span class="text-[11px] text-text-secondary block">Target Identifier</span>
            <span class="font-mono font-semibold text-primary">{{ selectedLog.target_id || '—' }}</span>
          </div>
        </div>

        <!-- Structured Details / Changed Fields (Sanitized) -->
        <div>
          <label class="block text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-1">
            Sanitized Event Payload & Modifications
          </label>
          <pre class="p-3.5 rounded-[6px] bg-[#203431] text-[#E1EEEA] text-[11px] font-mono overflow-x-auto max-h-56 leading-relaxed select-all">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
          <span class="text-[10px] text-text-secondary mt-1 block font-mono">
            * Passwords, tokens, and raw APAAR numbers are cryptographically masked or redacted from audit storage.
          </span>
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          @click="selectedLog = null"
          class="px-4 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium"
        >
          Close
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { auditLogsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import ModalDialog from '@/components/common/ModalDialog.vue';
import {
  Search,
  Loader2,
  ExternalLink
} from 'lucide-vue-next';

const isLoading = ref(true);
const logs = ref<any[]>([]);
const totalLogs = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);

const searchQuery = ref('');
const selectedTarget = ref('');
const selectedAction = ref('');
const selectedRole = ref('');
const availableActions = ref<string[]>([]);

const selectedLog = ref<any | null>(null);

let debounceTimer: any = null;

function formatActionLabel(action: string): string {
  if (!action) return '';
  return action
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatRole(role: string): string {
  if (!role) return '';
  return role.replace(/_/g, ' ');
}

function getActionBadgeClass(action: string, outcome: string): string {
  if (outcome === 'FAILED') {
    return 'bg-critical-bg text-critical border-critical/30';
  }
  if (action.includes('CREATED') || action.includes('COMMITTED') || action.includes('RESOLVED')) {
    return 'bg-success-bg text-success border-success/30';
  }
  if (action.includes('UPDATED') || action.includes('CHANGED')) {
    return 'bg-caution-bg text-caution border-caution/30';
  }
  return 'bg-primary-soft text-primary border-primary/20';
}

function formatDate(iso: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function openLogDetails(log: any) {
  selectedLog.value = log;
}

async function fetchLogs(page = 1) {
  isLoading.value = true;
  currentPage.value = page;

  try {
    const params: any = {
      page,
      per_page: 20
    };
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim();
    if (selectedTarget.value) params.target_type = selectedTarget.value;
    if (selectedAction.value) params.action = selectedAction.value;
    if (selectedRole.value) params.role = selectedRole.value;

    const res = await auditLogsApi.list(params);
    logs.value = res.data.logs || [];
    totalLogs.value = res.data.total || 0;
    totalPages.value = res.data.pages || 1;

    if (res.data.available_actions && res.data.available_actions.length > 0) {
      availableActions.value = res.data.available_actions;
    }
  } catch (err) {
    console.error('Failed to load audit logs', err);
  } finally {
    isLoading.value = false;
  }
}

function debouncedFetchLogs() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchLogs(1);
  }, 300);
}

onMounted(() => {
  fetchLogs(1);
});
</script>
