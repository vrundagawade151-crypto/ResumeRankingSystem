import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getJobs } from '../api';
import Navbar from '../components/Navbar';
import ApplyModal from '../components/ApplyModal';
import './CandidateDashboard.css';

export default function CandidateDashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applyJob, setApplyJob] = useState(null);

  useEffect(() => {
    getJobs()
      .then((res) => setJobs(res.data.jobs || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  const profile = JSON.parse(localStorage.getItem('profile') || '{}');

  return (
    <div className="candidate-dashboard">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="candidate" />
      <div className="dashboard-header">
        <div className="container">
          <h1>Welcome, {profile.name || 'Candidate'}</h1>
          <p>Browse and apply to jobs that match your skills</p>
        </div>
      </div>
      <div className="container dashboard-content">
        <section className="jobs-section">
          <h2>Available Jobs</h2>
          {loading ? (
            <p>Loading jobs...</p>
          ) : jobs.length === 0 ? (
            <p className="empty-state">No jobs posted yet. Check back later!</p>
          ) : (
            <div className="jobs-grid">
              {jobs.map((job) => (
                <div key={job.id} className="job-card card">
                  <h3>{job.job_title}</h3>
                  <p className="company">{job.company_name}</p>
                  <div className="job-meta">
                    <span>Skills: {job.required_skills}</span>
                    <span>Exp: {job.experience_required || 'Not specified'}</span>
                  </div>
                  <p className="job-desc">{job.job_description?.slice(0, 120)}...</p>
                  <button
                    className="btn btn-primary"
                    onClick={() => setApplyJob(job)}
                  >Apply Now</button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
      {applyJob && (
        <ApplyModal
          job={applyJob}
          onClose={() => setApplyJob(null)}
          onSuccess={() => setApplyJob(null)}
        />
      )}
    </div>
  );
}
