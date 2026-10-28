import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [selectedRole, setSelectedRole] = useState('inst_operator');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await authService.login(selectedRole);
      onLoginSuccess(data.user);

      // Redirect according to role
      if (data.user.role === 'aicte_admin') {
        navigate('/aicte-dashboard');
      } else if (data.user.role === 'verifier') {
        navigate('/verify');
      } else if (data.user.role === 'auditor') {
        navigate('/audit-log');
      } else {
        navigate('/institution-dashboard');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full border border-govborder bg-white p-6 sm:p-8">
        <div className="text-center mb-6">
          <div className="w-12 h-12 border border-govborder bg-gray-50 flex items-center justify-center mx-auto text-xs font-bold text-navy-800 mb-3">
            AICTE
          </div>
          <h1 className="text-lg font-bold text-navy-800">Single Sign-On (SSO) Authentication</h1>
          <p className="text-xs text-gray-600 mt-1">National Technical Education Portal Login</p>
        </div>

        {error && (
          <div className="mb-4 text-xs text-red-700 bg-red-50 border border-red-200 p-2 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSignIn} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Select Demo Identity / Keycloak Account:
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full text-xs border border-govborder p-2 focus:outline-none focus:border-navy-800 bg-white"
            >
              <option value="inst_operator">Institution Operator (DIAET - Upload & Edit)</option>
              <option value="inst_admin">Institution Admin (DIAET - Director / Resolve)</option>
              <option value="aicte_admin">AICTE Administrator (National Analytics)</option>
              <option value="verifier">Credential Verifier (Verification Officer)</option>
              <option value="auditor">Security Compliance Auditor (Audit Logs)</option>
            </select>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-navy-800 hover:bg-navy-900 text-white text-xs font-semibold border border-navy-900 transition-colors disabled:opacity-50"
            >
              {loading ? 'Authenticating via Keycloak...' : 'Sign in'}
            </button>
          </div>
        </form>

        <div className="mt-6 pt-4 border-t border-govborder text-center text-[11px] text-gray-500">
          Federated OpenID Connect (OIDC) identity provider with role & scope enforcement.
        </div>
      </div>
    </div>
  );
};
