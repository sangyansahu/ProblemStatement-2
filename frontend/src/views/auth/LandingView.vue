<template>
  <div class="min-h-screen bg-canvas text-text-primary flex flex-col antialiased">
    <!-- Institutional Top Navigation -->
    <header class="bg-surface border-b border-border sticky top-0 z-20 px-6 lg:px-12 py-3.5 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-sm bg-[#2B665B] border border-[#3E7A6E] flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-bronze" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <div class="font-bold text-[15px] tracking-wide text-text-primary leading-tight">
            AICTE
          </div>
          <div class="text-[11px] text-text-secondary leading-tight font-normal">
            All India Council for Technical Education
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <router-link
          to="/login"
          class="px-4 py-2 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[13px] font-medium transition-colors shadow-subtle flex items-center gap-1.5"
        >
          <span>Sign In to Portal</span>
          <ArrowRight class="w-4 h-4" />
        </router-link>
      </div>
    </header>

    <!-- Hero / Administrative Introduction Banner -->
    <section class="border-b border-border bg-[#F8F7F2] py-14 px-6 lg:px-12">
      <div class="max-w-4xl mx-auto">
        <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-sm bg-primary-soft text-primary text-[11px] font-mono font-medium border border-primary/20 mb-4">
          <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
          CENTRALIZED STUDENT REGISTRY & VERIFICATION SYSTEM
        </div>
        <h1 class="text-[28px] sm:text-[34px] font-semibold text-text-primary tracking-tight font-sans leading-snug">
          AICTE APAAR-Based Student Data Management & Verification Portal
        </h1>
        <p class="text-[15px] text-text-secondary mt-3 leading-relaxed font-normal">
          An authoritative digital infrastructure enabling technical and higher education institutions to submit student enrolment data in bulk, detect missing or inconsistent attributes, flag cross-institution duplicate candidate records, and track APAAR identity verification workflows.
        </p>

        <div class="mt-7 flex flex-wrap items-center gap-3.5">
          <router-link
            to="/login"
            class="px-5 py-2.5 rounded-[6px] bg-primary hover:bg-primary-hover text-[#FFFEFA] text-[13px] font-medium transition-colors flex items-center gap-2"
          >
            <span>Access Institutional Login</span>
            <ArrowRight class="w-4 h-4" />
          </router-link>
          <a
            href="/api/v1/uploads/template"
            download="aicte_student_upload_template.csv"
            class="px-4 py-2.5 rounded-[6px] bg-surface hover:bg-canvas text-text-primary border border-border text-[13px] font-medium transition-colors flex items-center gap-2"
          >
            <Download class="w-4 h-4 text-text-secondary" />
            <span>Download Official CSV Template</span>
          </a>
        </div>
      </div>
    </section>

    <!-- Operational Domain Columns -->
    <section class="max-w-6xl mx-auto px-6 py-12 flex-1 w-full">
      <div class="text-[12px] font-medium text-text-secondary uppercase tracking-wider mb-5">
        Core Portal Capabilities
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Institute Role Card -->
        <div class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle flex flex-col justify-between">
          <div>
            <div class="w-8 h-8 rounded-[6px] bg-primary-soft text-primary flex items-center justify-center mb-3.5">
              <Building2 class="w-4 h-4" />
            </div>
            <h3 class="text-[16px] font-semibold text-text-primary mb-2">
              Institution Portal
            </h3>
            <p class="text-[13px] text-text-secondary leading-relaxed font-normal mb-4">
              Authorized institutional representatives upload student records in bulk using standardized CSV templates, preview row-level validation errors, and resolve flagged discrepancies.
            </p>
            <ul class="space-y-2 text-[12px] text-text-secondary">
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Bulk CSV ingest with live syntax checks</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Row-by-row validation error reports</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Local student directory management</span>
              </li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-border/60">
            <span class="text-[11px] font-mono text-primary font-medium">Demo: institute_demo</span>
          </div>
        </div>

        <!-- APAAR Verification Card -->
        <div class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle flex flex-col justify-between">
          <div>
            <div class="w-8 h-8 rounded-[6px] bg-caution-bg text-caution flex items-center justify-center mb-3.5">
              <ShieldCheck class="w-4 h-4" />
            </div>
            <h3 class="text-[16px] font-semibold text-text-primary mb-2">
              Identity & Verification
            </h3>
            <p class="text-[13px] text-text-secondary leading-relaxed font-normal mb-4">
              Integrates privacy-preserving HMAC matching, AES encrypted storage, and format validation with a clear distinction between simulated checks and official registry verification.
            </p>
            <ul class="space-y-2 text-[12px] text-text-secondary">
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>12-digit APAAR format validation</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Masked identifiers for privacy protection</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Manual review override workflows</span>
              </li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-border/60">
            <span class="text-[11px] font-mono text-caution font-medium">Simulated Sandbox Active</span>
          </div>
        </div>

        <!-- Super Admin & AICTE Oversight Card -->
        <div class="bg-surface rounded-[8px] border border-border p-6 shadow-subtle flex flex-col justify-between">
          <div>
            <div class="w-8 h-8 rounded-[6px] bg-[#EBECE7] text-text-primary flex items-center justify-center mb-3.5">
              <Copy class="w-4 h-4" />
            </div>
            <h3 class="text-[16px] font-semibold text-text-primary mb-2">
              Conflict & Intake Oversight
            </h3>
            <p class="text-[13px] text-text-secondary leading-relaxed font-normal mb-4">
              Centralized monitoring for AICTE administrators to review cross-institution enrolment duplicates, track approved intake utilization, audit sensitive changes, and govern user roles.
            </p>
            <ul class="space-y-2 text-[12px] text-text-secondary">
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Cross-institution duplicate queue</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Approved intake capacity monitoring</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-primary shrink-0" />
                <span>Complete administrative audit trails</span>
              </li>
            </ul>
          </div>
          <div class="mt-6 pt-4 border-t border-border/60">
            <span class="text-[11px] font-mono text-text-secondary font-medium">Demo: superadmin_demo</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-border bg-surface py-6 px-6 lg:px-12 text-center text-[12px] text-text-secondary">
      <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          © 2026 All India Council for Technical Education (AICTE), Nelson Mandela Marg, Vasant Kunj, New Delhi-110070.
        </div>
        <div class="flex items-center gap-4 text-[11px] font-mono">
          <span>APAAR REGISTRY SPECIFICATION</span>
          <span>•</span>
          <router-link to="/login" class="text-primary hover:underline font-medium">Authorized Login</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, Download, Building2, ShieldCheck, Copy, CheckCircle2 } from 'lucide-vue-next';
</script>
