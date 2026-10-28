import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/api';

interface LayoutProps {
  children: React.ReactNode;
  user: any;
  onLogout: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [fontSize, setFontSize] = useState<'normal' | 'small' | 'large'>('normal');

  const handleLogout = () => {
    authService.logout();
    onLogout();
    navigate('/login');
  };

  const role = user?.role;

  // Determine navigation items based on role
  let navItems: { label: string; path: string }[] = [];

  if (role === 'institution_admin' || role === 'institution_operator') {
    navItems = [
      { label: 'Dashboard', path: '/institution-dashboard' },
      { label: 'Upload Students', path: '/upload-students' },
      { label: 'Student Records', path: '/student-records' },
      { label: 'Validation Cases', path: '/validation-cases' },
    ];
  } else if (role === 'aicte_admin') {
    navItems = [
      { label: 'National Dashboard', path: '/aicte-dashboard' },
      { label: 'Validation Cases', path: '/validation-cases' },
      { label: 'Reports', path: '/reports' },
    ];
  } else if (role === 'auditor') {
    navItems = [
      { label: 'Audit Log', path: '/audit-log' },
    ];
  } else if (role === 'verifier') {
    navItems = [
      { label: 'Verify Credential', path: '/verify' },
    ];
  }

  const fontClass = fontSize === 'small' ? 'text-xs' : fontSize === 'large' ? 'text-base' : 'text-sm';

  return (
    <div className={`min-h-screen bg-white flex flex-col font-sans ${fontClass}`}>
      {/* 1. Tricolour strip (saffron/white/green, 4 px) */}
      <div className="h-1 w-full flex">
        <div className="h-full flex-1 bg-[#FF9933]"></div>
        <div className="h-full flex-1 bg-white"></div>
        <div className="h-full flex-1 bg-[#138808]"></div>
      </div>

      {/* 2. Utility bar: skip-to-content and accessible A- A A+ control */}
      <div className="bg-gray-100 border-b border-govborder px-4 py-1 flex items-center justify-between text-xs text-gray-700">
        <a href="#main-content" className="skip-link sr-only focus:not-sr-only focus:underline text-navy-800 font-medium">
          Skip to main content
        </a>
        <div className="flex items-center gap-1.5 ml-auto">
          <span className="text-gray-500 mr-1">Text Size:</span>
          <button
            type="button"
            onClick={() => setFontSize('small')}
            className={`px-1.5 py-0.5 border border-govborder rounded ${fontSize === 'small' ? 'bg-navy-800 text-white' : 'bg-white text-gray-800'}`}
            title="Decrease text size"
          >
            A-
          </button>
          <button
            type="button"
            onClick={() => setFontSize('normal')}
            className={`px-1.5 py-0.5 border border-govborder rounded ${fontSize === 'normal' ? 'bg-navy-800 text-white' : 'bg-white text-gray-800'}`}
            title="Default text size"
          >
            A
          </button>
          <button
            type="button"
            onClick={() => setFontSize('large')}
            className={`px-1.5 py-0.5 border border-govborder rounded ${fontSize === 'large' ? 'bg-navy-800 text-white' : 'bg-white text-gray-800'}`}
            title="Increase text size"
          >
            A+
          </button>
        </div>
      </div>

      {/* 3. Header: Emblem placeholder + Two-line title | Right: User & Role & Logout */}
      <header className="border-b border-govborder bg-white px-4 py-3">
        <div className="max-w-[1200px] mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {/* Emblem placeholder */}
            <div className="w-12 h-12 border border-govborder bg-gray-50 flex items-center justify-center text-center font-bold text-navy-800 text-xs leading-none shrink-0">
              AICTE<br/>INDIA
            </div>
            <div>
              <div className="text-base sm:text-lg font-bold text-navy-800 leading-tight">
                All India Council for Technical Education
              </div>
              <div className="text-xs sm:text-sm text-gray-600 leading-tight">
                Student Data Management System
              </div>
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-3 text-xs sm:text-sm text-gray-700">
              <div className="text-right">
                <div className="font-semibold text-navy-800">{user.full_name || user.username}</div>
                <div className="text-gray-500 font-mono text-xs">Role: {user.role}</div>
              </div>
              <span className="text-gray-300">|</span>
              <button
                type="button"
                onClick={handleLogout}
                className="text-navy-800 hover:text-accent-saffron font-medium underline"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* 4. Horizontal navy navigation bar */}
      {navItems.length > 0 && (
        <nav className="bg-navy-800 text-white border-b border-navy-900 sticky top-0 z-30">
          <div className="max-w-[1200px] mx-auto flex overflow-x-auto">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2.5 text-xs sm:text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                    isActive
                      ? 'border-accent-saffron text-accent-saffron bg-navy-900 font-semibold'
                      : 'border-transparent text-gray-200 hover:text-white hover:bg-navy-700'
                  }`}
                >
                  {item.label}
                </NavLink>
              );
            })}
          </div>
        </nav>
      )}

      {/* 5. Main content area: fixed max-width container (~1200 px), generous whitespace */}
      <main id="main-content" className="flex-1 max-w-[1200px] w-full mx-auto p-4 sm:p-6">
        {children}
      </main>

      {/* 6. Footer: one line (copyright + "Prototype with synthetic data") */}
      <footer className="border-t border-govborder bg-gray-50 py-3 px-4 text-center text-xs text-gray-600">
        © 2026 All India Council for Technical Education (AICTE). Prototype with synthetic data.
      </footer>
    </div>
  );
};
