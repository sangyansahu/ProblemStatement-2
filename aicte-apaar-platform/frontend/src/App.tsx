import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { InstitutionDashboard } from './pages/InstitutionDashboard';
import { StudentRecords } from './pages/StudentRecords';
import { UploadStudents } from './pages/UploadStudents';
import { ValidationCases } from './pages/ValidationCases';
import { AICTEDashboard } from './pages/AICTEDashboard';
import { VerifyCredential } from './pages/VerifyCredential';
import { authService, analyticsService, verificationService } from './services/api';

// Minimal Reports view for aicte_admin
const ReportsPage: React.FC = () => {
  const [downloading, setDownloading] = useState(false);
  const [year, setYear] = useState('2025-26');

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await analyticsService.downloadEnrolmentReport(year);
    } catch (e) {
      alert('Failed to download report');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-base font-bold text-navy-800">National Enrolment Reports</h1>
      <p className="text-xs text-gray-600">Export verified enrolment records to standardized Excel workbook.</p>
      <div className="border border-govborder bg-white p-4 space-y-3">
        <label className="block text-xs font-semibold text-gray-700">Select Academic Cycle:</label>
        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          className="text-xs border border-govborder p-1.5 bg-white font-mono w-48"
        >
          <option value="2024-25">2024-25</option>
          <option value="2025-26">2025-26</option>
        </select>
        <div>
          <button
            type="button"
            onClick={handleDownload}
            disabled={downloading}
            className="py-2 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900"
          >
            {downloading ? 'Generating XLSX...' : 'Download Enrolment Report (XLSX)'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Minimal Audit Log view for auditor
const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    verificationService.getAuditLogs().then(setLogs).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-base font-bold text-navy-800">Immutable Audit Trail</h1>
      <p className="text-xs text-gray-600">System-wide governance logs for all data mutations and sensitive actions.</p>
      <div className="border border-govborder bg-white p-4">
        {loading ? (
          <div className="text-xs text-gray-500">Loading audit records...</div>
        ) : (
          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-gray-100 border-b border-govborder text-gray-700">
                <tr>
                  <th className="py-2 px-3 border border-govborder">Timestamp</th>
                  <th className="py-2 px-3 border border-govborder">Actor</th>
                  <th className="py-2 px-3 border border-govborder">Role</th>
                  <th className="py-2 px-3 border border-govborder">Action</th>
                  <th className="py-2 px-3 border border-govborder">Target</th>
                  <th className="py-2 px-3 border border-govborder">Outcome</th>
                  <th className="py-2 px-3 border border-govborder">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l, i) => (
                  <tr key={l.id} className={i % 2 === 1 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="py-1.5 px-3 border border-govborder font-mono">{new Date(l.timestamp).toLocaleString()}</td>
                    <td className="py-1.5 px-3 border border-govborder font-medium">{l.actor_id}</td>
                    <td className="py-1.5 px-3 border border-govborder font-mono text-[11px]">{l.actor_role}</td>
                    <td className="py-1.5 px-3 border border-govborder font-semibold text-navy-800">{l.action}</td>
                    <td className="py-1.5 px-3 border border-govborder font-mono">{l.target_reference}</td>
                    <td className="py-1.5 px-3 border border-govborder uppercase font-mono text-[11px] font-bold">{l.outcome}</td>
                    <td className="py-1.5 px-3 border border-govborder text-gray-600">{l.details || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<any | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  useEffect(() => {
    authService.getCurrentUser()
      .then((user) => setCurrentUser(user))
      .catch(() => setCurrentUser(null))
      .finally(() => setLoadingUser(false));
  }, []);

  const handleLoginSuccess = (user: any) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  if (loadingUser) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center text-xs text-gray-600 font-sans">
        Initializing AICTE Student Data Management Portal...
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public verification page without login */}
        <Route
          path="/verify/:ref?"
          element={
            <Layout user={currentUser} onLogout={handleLogout}>
              <VerifyCredential user={currentUser} />
            </Layout>
          }
        />

        {/* Login */}
        <Route
          path="/login"
          element={
            <Layout user={currentUser} onLogout={handleLogout}>
              <Login onLoginSuccess={handleLoginSuccess} />
            </Layout>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/institution-dashboard"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <InstitutionDashboard user={currentUser} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/upload-students"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <UploadStudents user={currentUser} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/student-records"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <StudentRecords user={currentUser} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/validation-cases"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <ValidationCases user={currentUser} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/aicte-dashboard"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <AICTEDashboard user={currentUser} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/reports"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <ReportsPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/audit-log"
          element={
            currentUser ? (
              <Layout user={currentUser} onLogout={handleLogout}>
                <AuditLogPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Default route redirect */}
        <Route
          path="*"
          element={
            currentUser ? (
              currentUser.role === 'aicte_admin' ? (
                <Navigate to="/aicte-dashboard" replace />
              ) : currentUser.role === 'verifier' ? (
                <Navigate to="/verify" replace />
              ) : currentUser.role === 'auditor' ? (
                <Navigate to="/audit-log" replace />
              ) : (
                <Navigate to="/institution-dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
};
