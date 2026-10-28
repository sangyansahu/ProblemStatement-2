import React, { useEffect, useState } from 'react';
import { studentsService } from '../services/api';

export const StudentRecords: React.FC<{ user: any }> = ({ user }) => {
  const [students, setStudents] = useState<any[]>([]);
  const [academicYear, setAcademicYear] = useState('');
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected student for detail / PATCH permitted fields
  const [selectedAdmission, setSelectedAdmission] = useState<any | null>(null);
  const [studentDetail, setStudentDetail] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit permitted fields: name, seat_category, status
  const [editName, setEditName] = useState('');
  const [editSeatCategory, setEditSeatCategory] = useState('');
  const [editStatus, setEditStatus] = useState('');
  const [patchMessage, setPatchMessage] = useState<string | null>(null);
  const [patchError, setPatchError] = useState<string | null>(null);
  const [isPatching, setIsPatching] = useState(false);

  const fetchRecords = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await studentsService.list({
        academic_year: academicYear || undefined,
        status: status || undefined,
        search: search || undefined,
      });
      setStudents(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to retrieve student records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [academicYear, status]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecords();
  };

  const handleRowClick = async (adm: any) => {
    setSelectedAdmission(adm);
    setPatchMessage(null);
    setPatchError(null);
    try {
      setDetailLoading(true);
      const detail = await studentsService.get(adm.student_id);
      setStudentDetail(detail);
      setEditName(detail.name || '');
      setEditSeatCategory(adm.seat_category || 'regular');
      setEditStatus(adm.status || 'enrolled');
    } catch (err: any) {
      setPatchError('Could not load student detail.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handlePatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdmission) return;
    setIsPatching(true);
    setPatchMessage(null);
    setPatchError(null);

    try {
      const updated = await studentsService.patch(selectedAdmission.id, {
        name: editName,
        seat_category: editSeatCategory,
        status: editStatus,
      });
      setPatchMessage('Record updated successfully.');
      setSelectedAdmission(updated);
      fetchRecords();
    } catch (err: any) {
      setPatchError(err?.response?.data?.detail || 'Update rejected by validation policy.');
    } finally {
      setIsPatching(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-base font-bold text-navy-800">
          Student Enrolment Registry
        </h1>
        <p className="text-xs text-gray-600">
          Search and view student enrolment records with masked APAAR tokens. Click a row to view details.
        </p>
      </div>

      {/* Filter and Search Bar (search bar permitted in Student Records) */}
      <div className="border border-govborder bg-white p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Search student number or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-govborder p-1.5 w-60 focus:outline-none focus:border-navy-800"
          />
          <button
            type="submit"
            className="py-1.5 px-3 bg-navy-800 text-white font-medium hover:bg-navy-900 border border-navy-900"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-gray-600">Cycle:</span>
            <select
              value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)}
              className="border border-govborder p-1.5 bg-white font-mono"
            >
              <option value="">All Cycles</option>
              <option value="2024-25">2024-25</option>
              <option value="2025-26">2025-26</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-gray-600">Status:</span>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="border border-govborder p-1.5 bg-white capitalize"
            >
              <option value="">All Statuses</option>
              <option value="enrolled">Enrolled</option>
              <option value="active">Active</option>
              <option value="withdrawn">Withdrawn</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {error && <div className="text-xs text-red-600">{error}</div>}

      {/* Student Records Table */}
      <div className="border border-govborder bg-white p-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-govborder text-gray-700">
                <th className="py-2 px-3 border border-govborder">Student Number</th>
                <th className="py-2 px-3 border border-govborder">APAAR Token (Masked)</th>
                <th className="py-2 px-3 border border-govborder">Programme</th>
                <th className="py-2 px-3 border border-govborder">Cycle</th>
                <th className="py-2 px-3 border border-govborder">Category</th>
                <th className="py-2 px-3 border border-govborder">Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-500 border border-govborder">
                    Loading records...
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-500 border border-govborder">
                    No student records matching criteria.
                  </td>
                </tr>
              ) : (
                students.map((adm, idx) => (
                  <tr
                    key={adm.id}
                    onClick={() => handleRowClick(adm)}
                    className={`cursor-pointer transition-colors ${
                      selectedAdmission?.id === adm.id
                        ? 'bg-amber-50 font-medium'
                        : idx % 2 === 1
                        ? 'bg-gray-50 hover:bg-gray-100'
                        : 'bg-white hover:bg-gray-50'
                    }`}
                  >
                    <td className="py-2 px-3 border border-govborder font-mono font-medium text-navy-800">
                      {adm.student_number}
                    </td>
                    <td className="py-2 px-3 border border-govborder font-mono text-gray-600">
                      {/* Masked identifier token (last 4 chars only) */}
                      ****-{adm.student_id ? adm.student_id.slice(-4) : 'SIM'}
                    </td>
                    <td className="py-2 px-3 border border-govborder">
                      {adm.course_code} - {adm.programme_name}
                    </td>
                    <td className="py-2 px-3 border border-govborder font-mono">{adm.academic_year}</td>
                    <td className="py-2 px-3 border border-govborder capitalize">{adm.seat_category}</td>
                    <td className="py-2 px-3 border border-govborder font-mono font-semibold uppercase text-[11px]">
                      {adm.status}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Read-Only Detail & Permitted Fields PATCH Panel */}
      {selectedAdmission && (
        <div className="border border-govborder bg-white p-4">
          <div className="flex items-center justify-between pb-2 border-b border-govborder mb-4">
            <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider">
              Student Record Detail (Student #{selectedAdmission.student_number})
            </h2>
            <button
              type="button"
              onClick={() => setSelectedAdmission(null)}
              className="text-xs text-gray-500 hover:text-gray-800"
            >
              Close Detail
            </button>
          </div>

          {detailLoading ? (
            <div className="text-xs text-gray-500">Loading profile details...</div>
          ) : (
            <div className="space-y-4">
              {/* Read-only permitted fields */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-gray-50 border border-gray-200 p-3">
                <div>
                  <div className="text-gray-500 text-[11px]">Masked APAAR Token</div>
                  <div className="font-mono font-bold text-navy-800">
                    {studentDetail?.apaar_token_masked || 'SIM-****'}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 text-[11px]">Institution</div>
                  <div>{selectedAdmission.institution_name || 'Enrolled Institution'}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-[11px]">Programme</div>
                  <div>{selectedAdmission.course_code} ({selectedAdmission.programme_name})</div>
                </div>
                <div>
                  <div className="text-gray-500 text-[11px]">Admission Date</div>
                  <div className="font-mono">{selectedAdmission.admission_date || '—'}</div>
                </div>
              </div>

              {/* PATCH form for permitted fields only */}
              <form onSubmit={handlePatch} className="space-y-3 pt-2">
                <div className="text-xs font-bold text-navy-800">
                  Update Permitted Attributes:
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Student Name:</label>
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="w-full text-xs border border-govborder p-1.5 focus:outline-none focus:border-navy-800 bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Seat Category:</label>
                    <select
                      value={editSeatCategory}
                      onChange={(e) => setEditSeatCategory(e.target.value)}
                      className="w-full text-xs border border-govborder p-1.5 focus:outline-none focus:border-navy-800 bg-white"
                    >
                      <option value="regular">Regular</option>
                      <option value="supernumerary">Supernumerary</option>
                      <option value="nri">NRI</option>
                      <option value="oci">OCI</option>
                      <option value="fn">Foreign National (FN)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Enrolment Status:</label>
                    <select
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value)}
                      className="w-full text-xs border border-govborder p-1.5 focus:outline-none focus:border-navy-800 bg-white"
                    >
                      <option value="enrolled">Enrolled</option>
                      <option value="active">Active</option>
                      <option value="withdrawn">Withdrawn</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>

                {patchMessage && <div className="text-xs text-green-700">{patchMessage}</div>}
                {patchError && <div className="text-xs text-red-600">{patchError}</div>}

                <div>
                  <button
                    type="submit"
                    disabled={isPatching}
                    className="py-1.5 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900 disabled:opacity-50"
                  >
                    {isPatching ? 'Saving Changes...' : 'Save Permitted Changes'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
