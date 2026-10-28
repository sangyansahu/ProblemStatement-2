import React, { useEffect, useState } from 'react';
import { analyticsService, api } from '../services/api';

export const InstitutionDashboard: React.FC<{ user: any }> = ({ user }) => {
  const [data, setData] = useState<any>(null);
  const [recentUploads, setRecentUploads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const analytics = await analyticsService.getInstitution();
        setData(analytics);

        // Fetch last 5 uploads
        const uploadsRes = await api.get('/uploads');
        setRecentUploads((uploadsRes.data || []).slice(0, 5));
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load institution dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  if (loading) {
    return <div className="p-4 text-xs text-gray-600">Loading institution dashboard data...</div>;
  }

  if (error) {
    return <div className="p-4 text-xs text-red-600">Error: {error}</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-base font-bold text-navy-800">
          Institution Operational Dashboard
        </h1>
        <p className="text-xs text-gray-600">
          {data?.institution_name || 'Affiliated Technical Institution'}
        </p>
      </div>

      {/* 1. Table of Programmes */}
      <div className="border border-govborder bg-white p-4">
        <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider mb-3">
          Approved Programmes & Capacity Utilisation
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-govborder text-gray-700">
                <th className="py-2 px-3 border border-govborder">Course Code</th>
                <th className="py-2 px-3 border border-govborder">Programme Name</th>
                <th className="py-2 px-3 border border-govborder">Academic Year</th>
                <th className="py-2 px-3 border border-govborder text-right">Approved Intake</th>
                <th className="py-2 px-3 border border-govborder text-right">Extra Seats</th>
                <th className="py-2 px-3 border border-govborder text-right">Reported Enrolment</th>
                <th className="py-2 px-3 border border-govborder text-right">Utilisation %</th>
              </tr>
            </thead>
            <tbody>
              {(!data?.programmes || data.programmes.length === 0) ? (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-gray-500 border border-govborder">
                    No approved programmes registered for this institution.
                  </td>
                </tr>
              ) : (
                data.programmes.map((prog: any, idx: number) => (
                  <tr key={prog.id} className={idx % 2 === 1 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="py-2 px-3 border border-govborder font-mono font-medium text-navy-800">
                      {prog.course_code}
                    </td>
                    <td className="py-2 px-3 border border-govborder">{prog.programme_name}</td>
                    <td className="py-2 px-3 border border-govborder font-mono">{prog.academic_year}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono">{prog.approved_intake}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono">{prog.approved_extra_seats}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono font-bold text-navy-800">
                      {prog.enrolled_count}
                    </td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono font-bold">
                      <span className={prog.utilisation_pct > 100 ? 'text-red-700' : 'text-gray-900'}>
                        {prog.utilisation_pct}%
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2. List of the last 5 uploads with status */}
      <div className="border border-govborder bg-white p-4">
        <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider mb-3">
          Last 5 Student Data Uploads
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-govborder text-gray-700">
                <th className="py-2 px-3 border border-govborder">File Name</th>
                <th className="py-2 px-3 border border-govborder">Cycle</th>
                <th className="py-2 px-3 border border-govborder text-right">Total Rows</th>
                <th className="py-2 px-3 border border-govborder text-right">Accepted</th>
                <th className="py-2 px-3 border border-govborder text-right">Rejected</th>
                <th className="py-2 px-3 border border-govborder text-right">Flagged</th>
                <th className="py-2 px-3 border border-govborder">Status</th>
                <th className="py-2 px-3 border border-govborder">Uploaded At</th>
              </tr>
            </thead>
            <tbody>
              {recentUploads.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-4 text-center text-gray-500 border border-govborder">
                    No student uploads on record.
                  </td>
                </tr>
              ) : (
                recentUploads.map((u: any, idx: number) => (
                  <tr key={u.id} className={idx % 2 === 1 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="py-2 px-3 border border-govborder font-medium text-navy-800">{u.file_name}</td>
                    <td className="py-2 px-3 border border-govborder font-mono">{u.academic_year}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono">{u.total_rows}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono text-green-700">{u.accepted_rows}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono text-red-700">{u.rejected_rows}</td>
                    <td className="py-2 px-3 border border-govborder text-right font-mono text-amber-700">{u.flagged_rows}</td>
                    <td className="py-2 px-3 border border-govborder">
                      <span className="font-mono uppercase font-bold text-[11px] text-navy-800">
                        {u.status}
                      </span>
                    </td>
                    <td className="py-2 px-3 border border-govborder text-gray-600 font-mono text-[11px]">
                      {new Date(u.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
