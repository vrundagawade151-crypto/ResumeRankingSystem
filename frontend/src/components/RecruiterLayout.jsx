import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import './RecruiterLayout.css';

const navItems = [
  { path: '/recruiter', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { path: '/recruiter/jobs/new', label: 'Post Job', icon: 'M12 6v6m0 0v6m0-6h6m-6 0H6' },
  { path: '/recruiter', label: 'Manage Jobs', icon: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { path: '/recruiter', label: 'Applicants', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
  { path: '/recruiter', label: 'Resume Screening', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' },
  { path: '/recruiter', label: 'Analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
];

export default function RecruiterLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const isActive = (path, label) => {
    if (path === '/recruiter/jobs/new') return location.pathname === '/recruiter/jobs/new';
    if (label === 'Dashboard') return location.pathname === '/recruiter';
    if (label === 'Manage Jobs') return location.pathname === '/recruiter';
    if (label === 'Applicants') return location.pathname.includes('/applicants');
    if (label === 'Resume Screening') return location.pathname.includes('/ranking');
    return location.pathname === path;
  };

  return (
    <div className="recruiter-layout">
      <aside className="recruiter-sidebar">
        <Link to="/" className="sidebar-brand">
          <span className="brand-icon">📋</span>
          <span>ResumeScreen AI</span>
        </Link>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.label}
              to={item.path}
              className={`sidebar-item ${isActive(item.path, item.label) ? 'active' : ''}`}
            >
              <svg className="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
              </svg>
              <span>{item.label}</span>
            </Link>
          ))}
          <button type="button" className="sidebar-item sidebar-logout" onClick={handleLogout}>
            <svg className="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Logout</span>
          </button>
        </nav>
      </aside>
      <div className="recruiter-main">
        <header className="recruiter-header">
          <div className="header-search">
            <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="search" placeholder="Search jobs, applicants..." className="search-input" />
          </div>
          <div className="header-actions">
            <button type="button" className="header-icon-btn" aria-label="Notifications">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="notification-dot" />
            </button>
            <div className="header-profile">
              <div className="profile-avatar">
                {(profile.name || user?.name || user?.email || 'R').charAt(0).toUpperCase()}
              </div>
              <div className="profile-info">
                <span className="profile-name">{profile.name || user?.name || 'Recruiter'}</span>
                <span className="profile-role">{profile.company_name || 'Company'}</span>
              </div>
            </div>
          </div>
        </header>
        <main className="recruiter-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
