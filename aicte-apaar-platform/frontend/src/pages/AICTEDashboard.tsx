import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { analyticsService, validationService } from '../services/api';

export const AICTEDashboard: React.FC<{ user: any }> = ({ user }) => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [recentCases, setRecentCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      const [anData, casesData] = await Promise.all([
        analyticsService.getNational(),
        validationService.listCases(),
      ]);
      setAnalytics(anData);
      setRecentCases((casesData || []).slice(0, 10));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to retrieve national analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Poll every 30 s from the frontend, no websockets
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-4 text-xs text-gray-600">Loading national analytics...</div>;
  }

  if (error) {
    return <div className="p-4 text-xs text-red-600">Error: {error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-base font-bold text-navy-800">
            National Enrolment & Compliance Monitoring Overview
          </h1>
          <p className="text-xs text-gray-600">
            System-wide operational oversight of technical education enrolments and data integrity.
          </p>
        </div>

        {/* Visible note: "Prototype - synthetic data." */}
        <div className="text-xs font-mono font-semibold text-accent-saffron border border-amber-300 bg-amber-50 px-2.5 py-1 inline-block self-start sm:self-auto">
          Prototype - synthetic data.
        </div>
      </div>

      {/* 4 Metric Figures (institutions reporting, students reported, records flagged, pending reviews) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="border border-govborder bg-white p-4">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">
            Institutions Reporting
          </div>
          <div className="text-2xl font-bold font-mono text-navy-800 mt-1">
            {analytics?.institutions_reporting || 0}
          </div>
          <div className="text-[11px] text-gray-500 mt-1">Affiliated technical colleges</div>
        </div>

        <div className="border border-govborder bg-white p-4">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">
            Students Reported
          </div>
          <div className="text-2xl font-bold font-mono text-navy-800 mt-1">
            {analytics?.students_reported || 0}
          </div>
          <div className="text-[11px] text-gray-500 mt-1">Centralized student records</div>
        </div>

        <div className="border border-govborder bg-white p-4">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">
            Records Flagged
          </div>
          <div className="text-2xl font-bold font-mono text-amber-700 mt-1">
            {analytics?.records_flagged || 0}
          </div>
          <div className="text-[11px] text-gray-500 mt-1">Discrepancies identified</div>
        </div>

        <div className="border border-govborder bg-white p-4">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider">
            Pending Reviews
          </div>
          <div className="text-2xl font-bold font-mono text-red-700 mt-1">
            {analytics?.pending_reviews || 0}
          </div>
          <div className="text-[11px] text-gray-500 mt-1">Open validation cases</div>
        </div>
      </div>

      {/* ONE Recharts Bar Chart of Enrolment by Academic Year */}
      <div className="border border-govborder bg-white p-4">
        <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider mb-3">
          Enrolment by Academic Cycle
        </h2>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={analytics?.enrolment_by_year || []}
              margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
              <XAxis dataKey="academic_year" stroke="#4B5563" fontSize={12} tickLine={false} />
              <YAxis stroke="#4B5563" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#D1D5DB', fontSize: '12px' }}
                cursor={{ fill: '#F3F4F6' }}
              />
              <Bar dataKey="enrolment_count" fill="#1F3A68" name="Active Enrolments" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table of the 10 most recent validation cases */}
      <div className="border border-govborder bg-white p-4">
        <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider mb-3">
          10 Most Recent Validation Discrepancies
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-govborder text-gray-700">
                <th className="py-2 px-3 border border-govborder">Rule Code</th>
                <th className="py-2 px-3 border border-govborder">Severity</th>
                <th className="py-2 px-3 border border-govborder">Institution</th>
                <th className="py-2 px-3 border border-govborder">Cycle</th>
                <th className="py-2 px-3 border border-govborder">Description / Message</th>
                <th className="py-2 px-3 border border-govborder">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentCases.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-500 border border-govborder">
                    No recent validation cases recorded.
                  </td>
                </tr>
              ) : (
                recentCases.map((c, idx) => (
                  <tr key={c.id} className={idx % 2 === 1 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="py-2 px-3 border border-govborder font-mono font-medium text-navy-800">
                      {c.rule_code}
                    </td>
                    <td className="py-2 px-3 border border-govborder">
                      <span
                        className={`font-semibold text-[11px] uppercase ${
                          c.severity === 'error'
                            ? 'text-red-700'
                            : c.severity === 'warning'
                            ? 'text-amber-700'
                            : 'text-gray-700'
                        }`}
                      >
                        {c.severity}
                      </span>
                    </td>
                    <td className="py-2 px-3 border border-govborder font-medium">
                      {c.institution_name || 'Affiliated Institute'}
                    </td>
                    <td className="py-2 px-3 border border-govborder font-mono">{c.academic_year}</td>
                    <td className="py-2 px-3 border border-govborder text-gray-800">{c.message}</td>
                    <td className="py-2 px-3 border border-govborder font-mono font-bold uppercase text-[11px]">
                      {c.status}
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
