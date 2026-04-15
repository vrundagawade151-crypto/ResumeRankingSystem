import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

export default function Navbar({ user, role }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    const token = localStorage.getItem('token');
    fetch('/api/auth/logout', {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    }).finally(() => {
      localStorage.clear();
      navigate('/');
    });
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">📋</span>
          ResumeScreen AI
        </Link>
        <div className="navbar-links">
          {!user ? (
            <>
              <Link to="/role-selection" className="nav-link">Login</Link>
            </>
          ) : (
            <>
              {role === 'candidate' && <Link to="/candidate" className="nav-link">Dashboard</Link>}
              {role === 'recruiter' && (
                <>
                  <Link to="/recruiter" className="nav-link">Dashboard</Link>
                  <Link to="/recruiter/jobs/new" className="nav-link">Post Job</Link>
                </>
              )}
              {role === 'admin' && <Link to="/admin" className="nav-link">Admin</Link>}
              <span className="nav-user">{user?.email || user?.name}</span>
              <button onClick={handleLogout} className="btn btn-ghost btn-sm">Logout</button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
