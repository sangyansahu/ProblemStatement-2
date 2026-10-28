import React, { useState } from 'react';
import { uploadsService } from '../services/api';

export const UploadStudents: React.FC<{ user: any }> = ({ user }) => {
  const [file, setFile] = useState<File | null>(null);
  const [academicYear, setAcademicYear] = useState('2025-26');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [batch, setBatch] = useState<any>(null);
  const [results, setResults] = useState<any[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a student CSV or XLSX file to upload.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const resBatch = await uploadsService.uploadFile(file, academicYear);
      setBatch(resBatch);

      const resResults = await uploadsService.getResults(resBatch.id);
      setResults(resResults);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Upload processing failed.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!results || results.length === 0) return;
    const header = ['Row', 'Student Number', 'Masked APAAR', 'Rule Code', 'Severity', 'Status', 'Message'];
    const rows = results.map((r) => [
      r.row_number,
      r.student_number || '',
      r.apaar_token_masked || '',
      r.rule_code || '',
      r.severity || '',
      r.status || '',
      `"${(r.message || '').replace(/"/g, '""')}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [header.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `validation_report_${batch?.id || 'batch'}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-base font-bold text-navy-800">
          Upload Student Enrolment Records
        </h1>
        <p className="text-xs text-gray-600">
          Batch ingestion with synchronous row-level schema validation and capacity checks.
        </p>
      </div>

      {/* Upload Form Card */}
      <div className="border border-govborder bg-white p-4">
        <form onSubmit={handleUpload} className="space-y-4 max-w-xl">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Academic Cycle:
            </label>
            <select
              value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)}
              className="text-xs border border-govborder p-1.5 focus:outline-none focus:border-navy-800 bg-white w-48 font-mono"
            >
              <option value="2024-25">2024-25</option>
              <option value="2025-26">2025-26</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Select CSV or XLSX file:
            </label>
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileChange}
              className="block w-full text-xs text-gray-700 file:mr-3 file:py-1.5 file:px-3 file:border file:border-govborder file:text-xs file:bg-gray-100 file:text-gray-800 hover:file:bg-gray-200"
            />
            <p className="text-[11px] text-gray-500 mt-1">
              Limit: Maximum 10 MB and 5,000 rows. Plain text CSV or standard XLSX workbook.
            </p>
          </div>

          {/* Plain text of required columns */}
          <div className="border border-gray-200 bg-gray-50 p-2.5 text-xs text-gray-700 space-y-1">
            <div className="font-semibold text-navy-800">Required Column Headers:</div>
            <p className="font-mono text-[11px]">
              student_number, apaar_id, course_code, academic_year, seat_category
            </p>
            <div className="font-semibold text-navy-800 mt-1.5">Optional Column Headers:</div>
            <p className="font-mono text-[11px]">name, admission_date</p>
            <p className="text-[11px] text-gray-500">
              Permitted seat categories: regular, supernumerary, nri, oci, fn.
            </p>
          </div>

          {error && (
            <div className="text-xs text-red-600 bg-red-50 border border-red-200 p-2">
              {error}
            </div>
          )}

          <div>
            {/* ONE primary action button */}
            <button
              type="submit"
              disabled={isUploading || !file}
              className="py-2 px-5 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900 transition-colors disabled:opacity-50"
            >
              {isUploading ? 'Validating Batch...' : 'Upload'}
            </button>
          </div>
        </form>
      </div>

      {/* Row-Level Results Table */}
      {batch && (
        <div className="border border-govborder bg-white p-4 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-govborder gap-2">
            <div>
              <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider">
                Batch Validation Results (Checksum: {batch.file_checksum.slice(0, 10)}...)
              </h2>
              <div className="text-xs text-gray-600 mt-0.5 space-x-3">
                <span>Total: <strong>{batch.total_rows}</strong></span>
                <span className="text-green-700">Accepted: <strong>{batch.accepted_rows}</strong></span>
                <span className="text-red-700">Rejected: <strong>{batch.rejected_rows}</strong></span>
                <span className="text-amber-700">Flagged: <strong>{batch.flagged_rows}</strong></span>
              </div>
            </div>

            {/* ONE download report link */}
            <button
              type="button"
              onClick={handleDownloadReport}
              className="text-xs text-navy-800 underline font-semibold hover:text-accent-saffron self-start sm:self-auto"
            >
              Download report
            </button>
          </div>

          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="sticky top-0 bg-gray-100 z-10 border-b border-govborder text-gray-700">
                <tr>
                  <th className="py-2 px-3 border border-govborder w-16">Row</th>
                  <th className="py-2 px-3 border border-govborder">Student Number</th>
                  <th className="py-2 px-3 border border-govborder">APAAR (Masked)</th>
                  <th className="py-2 px-3 border border-govborder">Rule</th>
                  <th className="py-2 px-3 border border-govborder">Severity</th>
                  <th className="py-2 px-3 border border-govborder">Message</th>
                </tr>
              </thead>
              <tbody>
                {results.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-4 text-center text-gray-500 border border-govborder">
                      No results for this batch.
                    </td>
                  </tr>
                ) : (
                  results.map((r) => (
                    <tr
                      key={r.id}
                      className={
                        r.status === 'rejected'
                          ? 'bg-red-50/50'
                          : r.status === 'flagged'
                          ? 'bg-amber-50/50'
                          : 'bg-white'
                      }
                    >
                      <td className="py-1.5 px-3 border border-govborder font-mono">{r.row_number}</td>
                      <td className="py-1.5 px-3 border border-govborder font-mono font-medium">{r.student_number || '—'}</td>
                      <td className="py-1.5 px-3 border border-govborder font-mono text-gray-600">{r.apaar_token_masked || '—'}</td>
                      <td className="py-1.5 px-3 border border-govborder font-mono text-[11px]">{r.rule_code || '—'}</td>
                      <td className="py-1.5 px-3 border border-govborder">
                        <span
                          className={`font-semibold text-[11px] uppercase ${
                            r.severity === 'error'
                              ? 'text-red-700'
                              : r.severity === 'warning'
                              ? 'text-amber-700'
                              : 'text-green-700'
                          }`}
                        >
                          {r.severity}
                        </span>
                      </td>
                      <td className="py-1.5 px-3 border border-govborder text-gray-800">{r.message}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
