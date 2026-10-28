import React, { useEffect, useState } from 'react';
import { validationService } from '../services/api';

export const ValidationCases: React.FC<{ user: any }> = ({ user }) => {
  const [cases, setCases] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Single confirm modal on "Resolve case"
  const [activeCase, setActiveCase] = useState<any | null>(null);
  const [resolutionNote, setResolutionNote] = useState('');
  const [resolveAction, setResolveAction] = useState<'resolve' | 'dismiss'>('resolve');
  const [isResolving, setIsResolving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchCases = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await validationService.listCases({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
      });
      setCases(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to retrieve validation cases.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [statusFilter, severityFilter]);

  const openResolveDialog = (c: any) => {
    setActiveCase(c);
    setResolutionNote('');
    setResolveAction('resolve');
    setActionError(null);
  };

  const handleConfirmResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCase) return;
    if (!resolutionNote.trim() || resolutionNote.trim().length < 3) {
      setActionError('A substantive justification note (min 3 characters) is required.');
      return;
    }

    setIsResolving(true);
    setActionError(null);

    try {
      await validationService.resolveCase(activeCase.id, resolutionNote, resolveAction);
      setActiveCase(null);
      fetchCases();
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Failed to resolve validation case.');
    } finally {
      setIsResolving(false);
    }
  };

  const canResolve = user?.role === 'aicte_admin' || user?.role === 'institution_admin';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-base font-bold text-navy-800">
          Validation Discrepancies & Conflict Review Cases
        </h1>
        <p className="text-xs text-gray-600">
          Review exceptions flagged during batch ingestion, including capacity overages, duplicate candidates, and anomalies.
        </p>
      </div>

      {/* Filters Bar */}
      <div className="border border-govborder bg-white p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-gray-600">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-govborder p-1.5 bg-white font-mono"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-gray-600">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="border border-govborder p-1.5 bg-white uppercase font-mono"
            >
              <option value="">All Severities</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="notice">Notice</option>
            </select>
          </div>
        </div>

        <button
          type="button"
          onClick={fetchCases}
          className="text-navy-800 underline hover:text-accent-saffron text-xs font-semibold"
        >
          Refresh table
        </button>
      </div>

      {error && <div className="text-xs text-red-600">{error}</div>}

      {/* Cases Table */}
      <div className="border border-govborder bg-white p-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-govborder text-gray-700">
                <th className="py-2 px-3 border border-govborder">Rule Code</th>
                <th className="py-2 px-3 border border-govborder">Severity</th>
                <th className="py-2 px-3 border border-govborder">Programme</th>
                <th className="py-2 px-3 border border-govborder">Academic Cycle</th>
                <th className="py-2 px-3 border border-govborder">Description / Message</th>
                <th className="py-2 px-3 border border-govborder">Status</th>
                {canResolve && <th className="py-2 px-3 border border-govborder text-right">Action</th>}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-gray-500 border border-govborder">
                    Loading validation cases...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-gray-500 border border-govborder">
                    No validation cases on record.
                  </td>
                </tr>
              ) : (
                cases.map((c, idx) => (
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
                    <td className="py-2 px-3 border border-govborder font-mono">
                      {c.course_code || '—'}
                    </td>
                    <td className="py-2 px-3 border border-govborder font-mono">{c.academic_year}</td>
                    <td className="py-2 px-3 border border-govborder text-gray-800 max-w-sm">
                      {c.message}
                      {c.resolution_note && (
                        <div className="text-[11px] text-green-800 font-medium mt-1">
                          Note: {c.resolution_note} ({c.resolved_by})
                        </div>
                      )}
                    </td>
                    <td className="py-2 px-3 border border-govborder font-mono uppercase text-[11px] font-bold">
                      {c.status}
                    </td>
                    {canResolve && (
                      <td className="py-2 px-3 border border-govborder text-right">
                        {c.status === 'open' ? (
                          <button
                            type="button"
                            onClick={() => openResolveDialog(c)}
                            className="text-navy-800 hover:text-accent-saffron font-semibold underline"
                          >
                            Resolve
                          </button>
                        ) : (
                          <span className="text-gray-400 font-mono text-[11px]">Closed</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Single confirm modal on "Resolve case" */}
      {activeCase && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-govborder max-w-md w-full p-5 space-y-4 shadow-lg">
            <div className="border-b border-govborder pb-2">
              <h3 className="text-xs font-bold text-navy-800 uppercase tracking-wider">
                Confirm Case Resolution
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Rule: <strong className="font-mono text-navy-800">{activeCase.rule_code}</strong>
              </p>
            </div>

            <form onSubmit={handleConfirmResolve} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Resolution Decision:
                </label>
                <select
                  value={resolveAction}
                  onChange={(e: any) => setResolveAction(e.target.value)}
                  className="w-full text-xs border border-govborder p-1.5 bg-white font-mono"
                >
                  <option value="resolve">Confirm & Resolve (Legitimate correction / transfer)</option>
                  <option value="dismiss">Dismiss Case (False positive flag)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Justification Note (Mandatory):
                </label>
                <textarea
                  rows={3}
                  required
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                  placeholder="State the regulatory basis or administrative rationale for resolving this case..."
                  className="w-full text-xs border border-govborder p-2 focus:outline-none focus:border-navy-800"
                />
              </div>

              {actionError && <div className="text-xs text-red-600">{actionError}</div>}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-govborder">
                <button
                  type="button"
                  onClick={() => setActiveCase(null)}
                  className="py-1.5 px-3 text-xs border border-govborder hover:bg-gray-100 text-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isResolving}
                  className="py-1.5 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900 disabled:opacity-50"
                >
                  {isResolving ? 'Submitting...' : 'Confirm Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
