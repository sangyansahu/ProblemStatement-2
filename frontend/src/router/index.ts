import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/auth/LandingView.vue'),
    meta: { public: true, title: 'AICTE Student Registry Portal' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true, title: 'Portal Sign In' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboards/DashboardDispatcher.vue'),
    meta: { requiresAuth: true, title: 'Overview Dashboard' },
  },
  {
    path: '/my-institution',
    name: 'MyInstitution',
    component: () => import('@/views/institutions/InstitutionDetailView.vue'),
    meta: { requiresAuth: true, roles: ['institute'], title: 'My Institution' },
  },
  {
    path: '/institutions',
    name: 'Institutions',
    component: () => import('@/views/institutions/InstitutionDirectoryView.vue'),
    meta: { requiresAuth: true, roles: ['super_admin'], title: 'Institution Management' },
  },
  {
    path: '/institutions/:id',
    name: 'InstitutionDetail',
    component: () => import('@/views/institutions/InstitutionDetailView.vue'),
    meta: { requiresAuth: true, title: 'Institution Profile & Students' },
  },
  {
    path: '/students',
    name: 'Students',
    component: () => import('@/views/students/StudentDirectoryView.vue'),
    meta: { requiresAuth: true, roles: ['institute'], title: 'Student Directory' },
  },
  {
    path: '/students/:id',
    name: 'StudentDetail',
    component: () => import('@/views/students/StudentDetailView.vue'),
    meta: { requiresAuth: true, title: 'Student Record' },
  },
  {
    path: '/bulk-upload',
    name: 'BulkUpload',
    component: () => import('@/views/uploads/BulkUploadView.vue'),
    meta: { requiresAuth: true, roles: ['institute'], title: 'Bulk Student Upload' },
  },
  {
    path: '/verification',
    name: 'VerificationQueue',
    component: () => import('@/views/verification/VerificationQueueView.vue'),
    meta: { requiresAuth: true, title: 'Verification Management' },
  },
  {
    path: '/duplicate-review',
    name: 'DuplicateReview',
    component: () => import('@/views/duplicate/DuplicateReviewView.vue'),
    meta: { requiresAuth: true, title: 'Duplicate & Conflict Review' },
  },
  {
    path: '/enrolment-monitoring',
    name: 'EnrolmentMonitoring',
    component: () => import('@/views/enrolment/EnrolmentMonitoringView.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'], title: 'Enrolment & Intake Monitoring' },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/reports/ReportsView.vue'),
    meta: { requiresAuth: true, title: 'Reports & Analytics' },
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/notifications/NotificationsView.vue'),
    meta: { requiresAuth: true, title: 'Notifications Center' },
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('@/views/admin/UserManagementView.vue'),
    meta: { requiresAuth: true, roles: ['super_admin'], title: 'User Management' },
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: () => import('@/views/admin/AuditLogsView.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'super_admin'], title: 'Audit Trail' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/SettingsView.vue'),
    meta: { requiresAuth: true, title: 'Profile & System Settings' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () => {
      const token = localStorage.getItem('aicte_token');
      return token ? '/dashboard' : '/';
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('aicte_token');
  const userStr = localStorage.getItem('aicte_user');
  const isAuthenticated = !!token && !!userStr;
  let userRole: string | null = null;

  if (userStr) {
    try {
      userRole = JSON.parse(userStr)?.role;
    } catch {}
  }

  // Update document title
  if (to.meta.title) {
    document.title = `${to.meta.title} | AICTE APAAR Portal`;
  }

  // Redirect to login if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ path: '/login', query: { redirect: to.fullPath } });
  }

  // If authenticated and going to login, redirect to dashboard
  if (to.path === '/login' && isAuthenticated) {
    return next('/dashboard');
  }

  // Specific role redirection for removed routes:
  // Super Admin / Admin trying to open global /students -> redirect to /institutions or /dashboard
  if (to.path === '/students' && userRole !== 'institute') {
    return next(userRole === 'super_admin' ? '/institutions' : '/dashboard');
  }

  // Super Admin or Admin trying to open /bulk-upload -> redirect to /dashboard
  if (to.path === '/bulk-upload' && userRole !== 'institute') {
    return next('/dashboard');
  }

  // Admin trying to open /institutions directory -> redirect to /dashboard
  if (to.path === '/institutions' && userRole === 'admin') {
    return next('/dashboard');
  }

  // Check role-based restrictions
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!userRole || !to.meta.roles.includes(userRole)) {
      return next('/dashboard');
    }
  }

  next();
});

export default router;
