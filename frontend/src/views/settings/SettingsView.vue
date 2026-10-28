<template>
  <div class="space-y-6">
    <PageHeader
      title="Profile & System Settings"
      description="Manage your authorized administrative account profile, configure personal security credentials, and oversee platform parameters."
    />

    <!-- Section Navigation Tabs -->
    <div class="flex items-center gap-2 border-b border-border text-[13px]">
      <button
        type="button"
        @click="activeSection = 'profile'"
        :class="[
          'px-4 py-2.5 font-medium border-b-2 transition-colors flex items-center gap-2',
          activeSection === 'profile'
            ? 'border-primary text-primary bg-primary-soft/20'
            : 'border-transparent text-text-secondary hover:text-text-primary'
        ]"
      >
        <UserIcon class="w-4 h-4" />
        <span>My Profile</span>
      </button>

      <button
        type="button"
        @click="activeSection = 'security'"
        :class="[
          'px-4 py-2.5 font-medium border-b-2 transition-colors flex items-center gap-2',
          activeSection === 'security'
            ? 'border-primary text-primary bg-primary-soft/20'
            : 'border-transparent text-text-secondary hover:text-text-primary'
        ]"
      >
        <KeyRound class="w-4 h-4" />
        <span>Account Security</span>
      </button>

      <button
        type="button"
        @click="activeSection = 'system'"
        :class="[
          'px-4 py-2.5 font-medium border-b-2 transition-colors flex items-center gap-2',
          activeSection === 'system'
            ? 'border-primary text-primary bg-primary-soft/20'
            : 'border-transparent text-text-secondary hover:text-text-primary'
        ]"
      >
        <Sliders class="w-4 h-4" />
        <span>System Parameters</span>
      </button>
    </div>

    <!-- SECTION A: MY PROFILE (Section 3.4 A) -->
    <div v-if="activeSection === 'profile'" class="space-y-6">
      <div class="bg-surface border border-border rounded-[8px] p-6 shadow-subtle">
        <div class="flex items-center justify-between pb-4 mb-6 border-b border-border">
          <div>
            <h3 class="text-[15px] font-semibold text-text-primary">Personal Account Details</h3>
            <p class="text-[12px] text-text-secondary mt-0.5">
              Update your contact credentials and display details. Role and institutional assignment are strictly governed.
            </p>
          </div>
          <span class="text-[10px] font-mono px-2.5 py-1 rounded-sm bg-primary-soft text-primary font-bold uppercase tracking-wide">
            ROLE: {{ authStore.role?.replace('_', ' ') }}
          </span>
        </div>

        <!-- Success Toast Alert -->
        <div
          v-if="profileSuccess"
          class="mb-5 p-3.5 rounded-[6px] bg-success-bg border border-success/30 text-success text-[12px] flex items-center gap-2"
        >
          <CheckCircle2 class="w-4 h-4 shrink-0" />
          <span>{{ profileSuccess }}</span>
        </div>

        <!-- Error Alert -->
        <div
          v-if="profileError"
          class="mb-5 p-3.5 rounded-[6px] bg-critical-bg border border-critical/30 text-critical text-[12px] flex items-center gap-2"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ profileError }}</span>
        </div>

        <form @submit.prevent="handleSaveProfile" class="space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <!-- Full Name (Editable) -->
            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="full_name">
                Full Legal Name <span class="text-critical">*</span>
              </label>
              <input
                id="full_name"
                v-model="profileForm.full_name"
                type="text"
                required
                placeholder="Enter your official full name"
                class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
              />
            </div>

            <!-- Email Address (Editable) -->
            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="email">
                Official Email Address <span class="text-critical">*</span>
              </label>
              <input
                id="email"
                v-model="profileForm.email"
                type="email"
                required
                placeholder="name@organization.gov.in"
                class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
              />
            </div>

            <!-- Phone Number (Editable) -->
            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="phone">
                Contact Phone Number
              </label>
              <input
                id="phone"
                v-model="profileForm.phone"
                type="text"
                placeholder="+91-XX-XXXX-XXXX"
                class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-mono"
              />
            </div>

            <!-- Username (Read-Only) -->
            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1.5">
                Account Username / System ID
              </label>
              <input
                :value="authStore.user?.username"
                disabled
                type="text"
                class="w-full h-[40px] px-3 rounded-[6px] bg-canvas border border-border text-[13px] text-text-secondary font-mono cursor-not-allowed"
              />
              <span class="text-[10px] text-text-secondary mt-1 block">Account identifiers cannot be modified.</span>
            </div>

            <!-- Associated Institution (Read-Only) -->
            <div class="sm:col-span-2">
              <label class="block text-[12px] font-medium text-text-secondary mb-1.5">
                Institutional Affiliation / Jurisdiction
              </label>
              <input
                :value="authStore.user?.institution_name || 'Central AICTE Headquarters, New Delhi'"
                disabled
                type="text"
                class="w-full h-[40px] px-3 rounded-[6px] bg-canvas border border-border text-[13px] text-text-secondary cursor-not-allowed"
              />
            </div>
          </div>

          <!-- Actions -->
          <div class="pt-4 border-t border-border flex items-center justify-end gap-3">
            <button
              type="button"
              @click="resetProfileForm"
              class="px-4 py-2 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[12px] font-medium transition-colors"
            >
              Reset Form
            </button>
            <button
              type="submit"
              :disabled="isSavingProfile"
              class="px-5 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors flex items-center gap-2 shadow-subtle disabled:opacity-70"
            >
              <Loader2 v-if="isSavingProfile" class="w-4 h-4 animate-spin" />
              <span>{{ isSavingProfile ? 'Saving Changes...' : 'Save Profile Changes' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- SECTION B: ACCOUNT SECURITY (Section 3.4 B) -->
    <div v-else-if="activeSection === 'security'" class="space-y-6">
      <div class="bg-surface border border-border rounded-[8px] p-6 shadow-subtle max-w-2xl">
        <div class="pb-4 mb-6 border-b border-border">
          <h3 class="text-[15px] font-semibold text-text-primary">Change Password</h3>
          <p class="text-[12px] text-text-secondary mt-0.5">
            Passwords must contain at least 6 characters and should include numbers and symbols.
          </p>
        </div>

        <div
          v-if="passwordSuccess"
          class="mb-5 p-3.5 rounded-[6px] bg-success-bg border border-success/30 text-success text-[12px] flex items-center gap-2"
        >
          <CheckCircle2 class="w-4 h-4 shrink-0" />
          <span>{{ passwordSuccess }}</span>
        </div>

        <div
          v-if="passwordError"
          class="mb-5 p-3.5 rounded-[6px] bg-critical-bg border border-critical/30 text-critical text-[12px] flex items-center gap-2"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ passwordError }}</span>
        </div>

        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="current_password">
              Current Password <span class="text-critical">*</span>
            </label>
            <input
              id="current_password"
              v-model="passwordForm.current_password"
              type="password"
              required
              class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
            />
          </div>

          <div>
            <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="new_password">
              New Password <span class="text-critical">*</span>
            </label>
            <input
              id="new_password"
              v-model="passwordForm.new_password"
              type="password"
              required
              minlength="6"
              class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
            />
          </div>

          <div>
            <label class="block text-[12px] font-medium text-text-secondary mb-1.5" for="confirm_password">
              Confirm New Password <span class="text-critical">*</span>
            </label>
            <input
              id="confirm_password"
              v-model="passwordForm.confirm_password"
              type="password"
              required
              minlength="6"
              class="w-full h-[40px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary font-sans"
            />
          </div>

          <div class="pt-4 border-t border-border flex justify-end">
            <button
              type="submit"
              :disabled="isSavingPassword"
              class="px-5 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors flex items-center gap-2 shadow-subtle disabled:opacity-70"
            >
              <Loader2 v-if="isSavingPassword" class="w-4 h-4 animate-spin" />
              <span>{{ isSavingPassword ? 'Updating Password...' : 'Update Password' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- SECTION C: GLOBAL SYSTEM PARAMETERS (Section 3.4 C) -->
    <div v-else-if="activeSection === 'system'" class="space-y-6">
      <!-- Verification Architecture Sandbox Boundary Disclosure -->
      <div class="bg-surface border border-border rounded-[8px] p-6 shadow-subtle">
        <div class="flex items-start justify-between gap-4 pb-2 mb-4 border-b border-border">
          <div>
            <h3 class="text-[15px] font-semibold text-text-primary">
              APAAR Verification Architecture
            </h3>
            <p class="text-[12px] text-text-secondary mt-0.5">
              Distinction between local format validation and official identity verification.
            </p>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-caution-bg text-caution border border-caution/30 font-semibold uppercase">
            Simulated Sandbox Mode Active
          </span>
        </div>

        <div class="bg-canvas border border-border/80 rounded-[6px] p-4 text-[12px] text-text-secondary leading-relaxed space-y-2">
          <p>
            <strong class="text-text-primary">Verification Boundary:</strong> Student record validation and duplicate detection are handled directly within this portal. Official identity verification is conducted through authenticated national portals.
          </p>
          <p>
            The portal is currently operating in <strong class="text-text-primary">Demonstration Mode</strong> using protected test records. Live student identities and official verification services remain safeguarded.
          </p>
        </div>
      </div>

      <!-- Operational Parameters Form -->
      <div class="bg-surface border border-border rounded-[8px] p-6 shadow-subtle">
        <div class="flex items-center justify-between pb-2 mb-4 border-b border-border">
          <div>
            <h3 class="text-[15px] font-semibold text-text-primary">
              Platform Operational Thresholds
            </h3>
            <p class="text-[12px] text-text-secondary mt-0.5">
              {{ authStore.isSuperAdmin ? 'Configure platform thresholds, academic cycles, and data retention.' : 'View current administrative thresholds enforced across the portal.' }}
            </p>
          </div>
          <span v-if="!authStore.isSuperAdmin" class="text-[11px] text-text-secondary font-mono">
            Read-Only Access
          </span>
        </div>

        <div v-if="systemSuccess" class="mb-4 p-3 rounded-[6px] bg-success-bg border border-success/30 text-success text-[12px]">
          <span>✓ Operational settings successfully updated and committed to audit ledger.</span>
        </div>

        <form @submit.prevent="saveSystemSettings" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1">Active Academic Cycle</label>
              <select
                v-model="systemForm.current_academic_year"
                :disabled="!authStore.isSuperAdmin"
                class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary disabled:opacity-75 disabled:bg-canvas font-mono"
              >
                <option v-for="year in academicYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>

            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1">Max Bulk Upload Size (MB)</label>
              <input
                v-model.number="systemForm.max_upload_size_mb"
                :disabled="!authStore.isSuperAdmin"
                type="number"
                min="1"
                max="100"
                class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary disabled:opacity-75 disabled:bg-canvas font-mono"
              />
            </div>

            <div>
              <label class="block text-[12px] font-medium text-text-secondary mb-1">Data Retention Period (Days)</label>
              <input
                v-model.number="systemForm.data_retention_days"
                :disabled="!authStore.isSuperAdmin"
                type="number"
                min="365"
                max="3650"
                class="w-full h-[38px] px-3 rounded-[6px] bg-search-bg border border-border text-[13px] text-text-primary focus:outline-none focus:border-primary disabled:opacity-75 disabled:bg-canvas font-mono"
              />
            </div>
          </div>

          <div v-if="authStore.isSuperAdmin" class="pt-4 flex justify-end">
            <button
              type="submit"
              :disabled="isSavingSystem"
              class="px-5 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[12px] font-medium transition-colors flex items-center gap-2 disabled:opacity-70"
            >
              <Loader2 v-if="isSavingSystem" class="w-4 h-4 animate-spin" />
              <span>{{ isSavingSystem ? 'Saving...' : 'Save Configuration Changes' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { settingsApi } from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import {
  User as UserIcon,
  KeyRound,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-vue-next';

const authStore = useAuthStore();
const activeSection = ref<'profile' | 'security' | 'system'>('profile');

// Profile Form State
const profileForm = ref({
  full_name: '',
  email: '',
  phone: ''
});
const isSavingProfile = ref(false);
const profileSuccess = ref('');
const profileError = ref('');

// Password Form State
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
});
const isSavingPassword = ref(false);
const passwordSuccess = ref('');
const passwordError = ref('');

// Global System Parameters Form State
const academicYears = ref(['2023-2024', '2024-2025', '2025-2026', '2026-2027']);
const systemForm = ref({
  current_academic_year: '2025-2026',
  max_upload_size_mb: 16,
  data_retention_days: 1825,
});
const isSavingSystem = ref(false);
const systemSuccess = ref(false);

function resetProfileForm() {
  if (authStore.user) {
    profileForm.value.full_name = authStore.user.full_name || '';
    profileForm.value.email = authStore.user.email || '';
    profileForm.value.phone = authStore.user.phone || '';
  }
}

async function handleSaveProfile() {
  profileSuccess.value = '';
  profileError.value = '';
  isSavingProfile.value = true;

  try {
    const res = await authStore.updateProfile({
      full_name: profileForm.value.full_name.trim(),
      email: profileForm.value.email.trim(),
      phone: profileForm.value.phone.trim()
    });

    if (res.success) {
      profileSuccess.value = 'Profile information saved successfully. Updated details are active across the portal.';
      setTimeout(() => { profileSuccess.value = ''; }, 5000);
    } else {
      profileError.value = res.message || 'Failed to save profile';
    }
  } catch (err: any) {
    profileError.value = err.message || 'An unexpected error occurred while saving profile';
  } finally {
    isSavingProfile.value = false;
  }
}

async function handleChangePassword() {
  passwordSuccess.value = '';
  passwordError.value = '';

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'New password and confirmation password do not match.';
    return;
  }

  isSavingPassword.value = true;

  try {
    const res = await authStore.changePassword({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    });

    if (res.success) {
      passwordSuccess.value = 'Password changed successfully.';
      passwordForm.value = { current_password: '', new_password: '', confirm_password: '' };
      setTimeout(() => { passwordSuccess.value = ''; }, 5000);
    } else {
      passwordError.value = res.message || 'Failed to change password';
    }
  } catch (err: any) {
    passwordError.value = err.message || 'An unexpected error occurred';
  } finally {
    isSavingPassword.value = false;
  }
}

async function loadSystemSettings() {
  try {
    const res = await settingsApi.get();
    if (res.data?.settings) {
      systemForm.value.current_academic_year = res.data.settings.current_academic_year || '2025-2026';
      systemForm.value.max_upload_size_mb = res.data.settings.max_upload_size_mb || 16;
      systemForm.value.data_retention_days = res.data.settings.data_retention_days || 1825;
      if (res.data.settings.academic_years) {
        academicYears.value = res.data.settings.academic_years;
      }
    }
  } catch (err) {
    console.error('Failed to load system settings', err);
  }
}

async function saveSystemSettings() {
  if (!authStore.isSuperAdmin) return;
  isSavingSystem.value = true;
  systemSuccess.value = false;

  try {
    await settingsApi.update(systemForm.value);
    systemSuccess.value = true;
    setTimeout(() => { systemSuccess.value = false; }, 4000);
  } catch (err) {
    console.error('Failed to update system settings', err);
  } finally {
    isSavingSystem.value = false;
  }
}

onMounted(() => {
  resetProfileForm();
  loadSystemSettings();
});
</script>
