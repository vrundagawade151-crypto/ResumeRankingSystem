import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecruiterJobs, updateJob } from '../api';
import './RecruiterDashboard.css';

export default function RecruiterDashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    getRecruiterJobs()
      .then((res) => setJobs(res.data.jobs || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    const notification = { id, message, type, timestamp: new Date() };
    setNotifications(prev => [notification, ...prev]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const handleToggleJobStatus = async (job) => {
    const newStatus = job.status === 'active' ? 'closed' : 'active';
    const action = newStatus === 'closed' ? 'deactivate' : 'activate';
    
    if (window.confirm(`Are you sure you want to ${action} "${job.job_title}"?`)) {
      try {
        await updateJob(job.id, { is_active: newStatus === 'active' });
        // Update local state
        setJobs(jobs.map(j => 
          j.id === job.id ? { ...j, status: newStatus } : j
        ));
        addNotification(`Job "${job.job_title}" has been ${action}d successfully!`, 'success');
      } catch (err) {
        addNotification('Failed to update job status', 'error');
      }
    }
  };

  const handleShareLinkedIn = (job) => {
    const jobUrl = `${window.location.origin}/job/${job.id}`;
    const message = `Check out this job opening: ${job.job_title} at ${job.company_name || 'Our Company'}. ${job.location ? `Location: ${job.location}. ` : ''}Apply now: ${jobUrl} #hiring #recruitment`;
    
    const linkedInShareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(jobUrl)}`;
    window.open(linkedInShareUrl, 'linkedin-share', 'width=600,height=400');
    
    addNotification(`Job "${job.job_title}" shared to LinkedIn!`, 'info');
  };

  const totalJobs = jobs.length;
  const totalApplicants = jobs.reduce((sum, j) => sum + (j.applicant_count || 0), 0);
  const shortlisted = 0;
  const aiScreened = 0;

  const statCards = [
    { label: 'Total Jobs Posted', value: totalJobs, icon: 'briefcase' },
    { label: 'Total Applicants', value: totalApplicants, icon: 'users' },
    { label: 'Shortlisted Candidates', value: shortlisted, icon: 'check' },
    { label: 'AI Screened Resumes', value: aiScreened, icon: 'sparkles' },
  ];

  return (
    <div className="recruiter-dashboard">
      <div className="dashboard-page-header">
        <h1>Dashboard</h1>
        <p>Manage your job postings and applicants</p>
      </div>

      <div className="stat-cards">
        {statCards.map((card) => (
          <div key={card.label} className="stat-card">
            <div className="stat-card-icon" data-icon={card.icon}>
              {card.icon === 'briefcase' && (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              )}
              {card.icon === 'users' && (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              )}
              {card.icon === 'check' && (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              )}
              {card.icon === 'sparkles' && (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
              )}
            </div>
            <div className="stat-card-content">
              <span className="stat-card-value">{card.value}</span>
              <span className="stat-card-label">{card.label}</span>
            </div>
          </div>
        ))}
      </div>

      <section className="jobs-section">
        <div className="jobs-section-header">
          <h2>Your Job Postings</h2>
          <Link to="/recruiter/jobs/new" className="btn btn-primary">+ Post New Job</Link>
        </div>

        {loading ? (
          <div className="jobs-loading">Loading...</div>
        ) : jobs.length === 0 ? (
          <div className="jobs-empty-state card">
            <p>No jobs yet. Create your first job posting!</p>
            <Link to="/recruiter/jobs/new" className="btn btn-primary">Post Your First Job</Link>
          </div>
        ) : (
          <div className="jobs-table-card card">
            <table className="jobs-table">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Experience</th>
                  <th>Location</th>
                  <th>Job Type</th>
                  <th>Applicants</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="job-title-cell">{job.job_title}</td>
                    <td>{job.experience_required || '-'}</td>
                    <td>{job.location || '-'}</td>
                    <td>{job.job_type || '-'}</td>
                    <td>{job.applicant_count || 0}</td>
                    <td>
                      <span className={`badge badge-${job.status}`}>{job.status}</span>
                      <button
                        type="button"
                        className={`btn btn-toggle-status ${job.status}`}
                        onClick={() => handleToggleJobStatus(job)}
                        title={job.status === 'active' ? 'Deactivate job' : 'Activate job'}
                      >
                        {job.status === 'active' ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                    <td>
                      <Link to={`/recruiter/jobs/${job.id}/applicants`} className="btn btn-view-applicants">
                        View Applicants
                      </Link>
                      <Link to={`/recruiter/jobs/${job.id}/ranking`} className="btn btn-ai-rank">AI Rank</Link>
                      <Link to={`/recruiter/reports/${job.id}`} className="btn btn-report">Report</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
