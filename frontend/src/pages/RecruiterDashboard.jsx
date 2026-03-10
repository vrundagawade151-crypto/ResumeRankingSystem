import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecruiterJobs } from '../api';
import Navbar from '../components/Navbar';
import './RecruiterDashboard.css';

export default function RecruiterDashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRecruiterJobs()
      .then((res) => setJobs(res.data.jobs || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  const profile = JSON.parse(localStorage.getItem('profile') || '{}');

  return (
    <div className="recruiter-dashboard">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="recruiter" />
      <div className="dashboard-header">
        <div className="container">
          <h1>Welcome, {profile.name || 'Recruiter'}</h1>
          <p>{profile.company_name || 'Company'} — Manage your job postings and applicants</p>
        </div>
      </div>
      <div className="container dashboard-content">
        <div className="dashboard-actions">
          <Link to="/recruiter/jobs/new" className="btn btn-primary">+ Post New Job</Link>
        </div>
        <section className="jobs-section">
          <h2>Your Job Postings</h2>
          {loading ? (
            <p>Loading...</p>
          ) : jobs.length === 0 ? (
            <p className="empty-state">No jobs yet. Create your first job posting!</p>
          ) : (
            <div className="jobs-table-wrap">
              <table className="jobs-table">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Applicants</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.id}>
                      <td>{job.job_title}</td>
                      <td>{job.company_name}</td>
                      <td>{job.applicant_count || 0}</td>
                      <td><span className={`badge badge-${job.status}`}>{job.status}</span></td>
                      <td>
                        <Link to={`/recruiter/jobs/${job.id}/applicants`} className="btn btn-ghost btn-sm">Applicants</Link>
                        <Link to={`/recruiter/jobs/${job.id}/ranking`} className="btn btn-primary btn-sm">AI Rank</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
