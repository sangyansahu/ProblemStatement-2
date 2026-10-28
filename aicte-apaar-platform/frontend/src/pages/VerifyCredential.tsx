import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { verificationService, studentsService } from '../services/api';

export const VerifyCredential: React.FC<{ user?: any }> = ({ user }) => {
  const { ref } = useParams<{ ref?: string }>();
  const navigate = useNavigate();

  // Public verify state
  const [searchRef, setSearchRef] = useState(ref || '');
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Issuer issue credential state
  const [students, setStudents] = useState<any[]>([]);
  const [selectedAdmissionId, setSelectedAdmissionId] = useState('');
  const [issuedCredential, setIssuedCredential] = useState<any | null>(null);
  const [isIssuing, setIsIssuing] = useState(false);
  const [issueError, setIssueError] = useState<string | null>(null);

  const performVerification = async (verifyRef: string) => {
    if (!verifyRef.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await verificationService.publicVerify(verifyRef.trim());
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Verification lookup failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ref) {
      setSearchRef(ref);
      performVerification(ref);
    }
  }, [ref]);

  // If logged in as issuer (institution_admin or operator), fetch students to permit single "Generate QR" action
  const canIssue = user?.role === 'institution_admin' || user?.role === 'institution_operator';

  useEffect(() => {
    if (canIssue) {
      studentsService.list({ status: 'enrolled' }).then((data) => {
        setStudents(data || []);
        if (data && data.length > 0) {
          setSelectedAdmissionId(data[0].id);
        }
      }).catch(() => {});
    }
  }, [canIssue]);

  const handleGenerateQR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdmissionId) return;
    setIsIssuing(true);
    setIssueError(null);
    try {
      const cred = await verificationService.createRequest(selectedAdmissionId);
      setIssuedCredential(cred);
    } catch (err: any) {
      setIssueError(err?.response?.data?.detail || 'Failed to issue credential.');
    } finally {
      setIsIssuing(false);
    }
  };

  const handleManualVerify = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchRef.trim()) {
      navigate(`/verify/${searchRef.trim()}`);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-base font-bold text-navy-800">
          Official Credential Verification Service
        </h1>
        <p className="text-xs text-gray-600">
          National public verification for academic enrolment credentials.
        </p>
      </div>

      {/* Manual lookup input if no ref or to check another */}
      <div className="border border-govborder bg-white p-4">
        <form onSubmit={handleManualVerify} className="flex gap-2">
          <input
            type="text"
            placeholder="Enter opaque verification reference (e.g. CR-xX_...)"
            value={searchRef}
            onChange={(e) => setSearchRef(e.target.value)}
            className="flex-1 text-xs border border-govborder p-2 focus:outline-none focus:border-navy-800 font-mono"
          />
          <button
            type="submit"
            className="py-2 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900"
          >
            Verify
          </button>
        </form>
      </div>

      {loading && <div className="text-xs text-gray-600 p-2">Verifying credential reference...</div>}
      {error && <div className="text-xs text-red-600 p-2">{error}</div>}

      {/* Public Result Card (institution, credential type, status) */}
      {result && (
        <div className="border border-govborder bg-white p-6 space-y-4">
          <div className="border-b border-govborder pb-3 flex items-center justify-between">
            <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider">
              Verification Outcome
            </h2>
            <span
              className={`font-mono text-xs uppercase font-bold px-2 py-0.5 border ${
                result.status === 'valid'
                  ? 'bg-green-50 border-green-300 text-green-800'
                  : result.status === 'revoked'
                  ? 'bg-red-50 border-red-300 text-red-800'
                  : 'bg-gray-100 border-gray-300 text-gray-700'
              }`}
            >
              {result.status}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-gray-100">
              <span className="text-gray-500">Issuing Institution:</span>
              <span className="font-semibold text-navy-800 text-right">{result.issuing_institution}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-100">
              <span className="text-gray-500">Credential Type:</span>
              <span className="font-medium text-gray-800">{result.credential_type}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-100">
              <span className="text-gray-500">Issued On:</span>
              <span className="font-mono text-gray-700">{result.issued_at || '—'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-gray-500">Verified Timestamp:</span>
              <span className="font-mono text-gray-700">{result.verified_at}</span>
            </div>
          </div>

          <div className="bg-gray-50 border border-govborder p-2.5 text-[11px] text-gray-500 text-center">
            Verification signed cryptographically via AICTE RS256 authority. Identity privacy protected.
          </div>
        </div>
      )}

      {/* For authorized issuers only: single "Generate QR" action */}
      {canIssue && (
        <div className="border border-govborder bg-white p-4 space-y-4">
          <div className="border-b border-govborder pb-2">
            <h2 className="text-xs font-bold text-navy-800 uppercase tracking-wider">
              Issue Verifiable Student Credential
            </h2>
            <p className="text-[11px] text-gray-500">
              Generate QR code and RS256 token encoding opaque verification reference only.
            </p>
          </div>

          <form onSubmit={handleGenerateQR} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Select Admitted Student:
              </label>
              <select
                value={selectedAdmissionId}
                onChange={(e) => setSelectedAdmissionId(e.target.value)}
                className="w-full text-xs border border-govborder p-2 bg-white"
              >
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.student_number} - {s.course_code} ({s.academic_year})
                  </option>
                ))}
              </select>
            </div>

            {issueError && <div className="text-xs text-red-600">{issueError}</div>}

            {/* ONE single action button */}
            <div>
              <button
                type="submit"
                disabled={isIssuing || students.length === 0}
                className="py-2 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900 disabled:opacity-50"
              >
                {isIssuing ? 'Generating QR...' : 'Generate QR'}
              </button>
            </div>
          </form>

          {issuedCredential && (
            <div className="border border-gray-200 bg-gray-50 p-4 text-center space-y-3">
              <div className="text-xs font-semibold text-navy-800">
                Official Credential Issued
              </div>
              <div className="inline-block p-2 bg-white border border-govborder">
                <img
                  src={issuedCredential.qr_data}
                  alt="Credential Verification QR"
                  className="w-40 h-40 mx-auto"
                />
              </div>
              <div className="text-[11px] text-gray-600 font-mono">
                Opaque Reference: <strong>{issuedCredential.opaque_reference}</strong>
              </div>
              <p className="text-[11px] text-gray-500">
                QR encodes: <code className="bg-gray-200 px-1 py-0.5">https://host/verify/{issuedCredential.opaque_reference}</code> (NO personal data in QR)
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
