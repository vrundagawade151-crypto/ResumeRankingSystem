import { useState, useEffect } from 'react';
import { getRecruiters, getCandidates, getAdminJobs, getStatistics } from '../api';
import Navbar from '../components/Navbar';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [recruiters, setRecruiters] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [rRes, cRes, jRes, sRes] = await Promise.all([
          getRecruiters(),
          getCandidates(),
          getAdminJobs(),
          getStatistics(),
        ]);
        setRecruiters(rRes.data.recruiters || []);
        setCandidates(cRes.data.candidates || []);
        setJobs(jRes.data.jobs || []);
        setStats(sRes.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="admin-dashboard">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="admin" />
      <div className="admin-header">
        <div className="container">
          <h1>Admin Dashboard</h1>
          <p>Manage recruiters, candidates, and job postings</p>
        </div>
      </div>
      <div className="container admin-content">
        <div className="admin-tabs">
          <button className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Overview</button>
          <button className={tab === 'recruiters' ? 'active' : ''} onClick={() => setTab('recruiters')}>Recruiters</button>
          <button className={tab === 'candidates' ? 'active' : ''} onClick={() => setTab('candidates')}>Candidates</button>
          <button className={tab === 'jobs' ? 'active' : ''} onClick={() => setTab('jobs')}>Jobs</button>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
            {tab === 'overview' && stats && (
              <div className="stats-grid">
                <div className="stat-card card">
                  <span className="stat-value">{stats.total_recruiters}</span>
                  <span className="stat-label">Recruiters</span>
                </div>
                <div className="stat-card card">
                  <span className="stat-value">{stats.total_candidates}</span>
                  <span className="stat-label">Candidates</span>
                </div>
                <div className="stat-card card">
                  <span className="stat-value">{stats.total_jobs}</span>
                  <span className="stat-label">Total Jobs</span>
                </div>
                <div className="stat-card card">
                  <span className="stat-value">{stats.active_jobs}</span>
                  <span className="stat-label">Active Jobs</span>
                </div>
                <div className="stat-card card">
                  <span className="stat-value">{stats.total_applications}</span>
                  <span className="stat-label">Applications</span>
                </div>
              </div>
            )}

            {tab === 'recruiters' && (
              <div className="data-table-wrap card">
                <h3>All Recruiters</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Company</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recruiters.map((r) => (
                      <tr key={r.id}>
                        <td>{r.id}</td>
                        <td>{r.name}</td>
                        <td>{r.email}</td>
                        <td>{r.company_name || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {tab === 'candidates' && (
              <div className="data-table-wrap card">
                <h3>All Candidates</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Skills</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidates.map((c) => (
                      <tr key={c.id}>
                        <td>{c.id}</td>
                        <td>{c.name}</td>
                        <td>{c.email}</td>
                        <td>{c.skills ? c.skills.slice(0, 50) + (c.skills.length > 50 ? '...' : '') : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {tab === 'jobs' && (
              <div className="data-table-wrap card">
                <h3>All Job Postings</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Company</th>
                      <th>Recruiter</th>
                      <th>Applicants</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((j) => (
                      <tr key={j.id}>
                        <td>{j.id}</td>
                        <td>{j.job_title}</td>
                        <td>{j.company_name}</td>
                        <td>{j.recruiter?.name || '-'}</td>
                        <td>{j.applicant_count || 0}</td>
                        <td><span className={`badge badge-${j.status}`}>{j.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
