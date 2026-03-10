import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../api';
import Navbar from '../components/Navbar';
import './JobPosting.css';

export default function JobPosting() {
  const navigate = useNavigate();
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const [form, setForm] = useState({
    job_title: '',
    company_name: profile.company_name || '',
    required_skills: '',
    experience_required: '',
    job_description: '',
    number_of_openings: 1,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await createJob(form);
      navigate('/recruiter');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-posting-page">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="recruiter" />
      <div className="container page-content">
        <h1>Post a New Job</h1>
        <div className="form-card card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Job Title *</label>
              <input
                value={form.job_title}
                onChange={(e) => setForm({ ...form, job_title: e.target.value })}
                placeholder="e.g. Senior Software Engineer"
                required
              />
            </div>
            <div className="form-group">
              <label>Company Name *</label>
              <input
                value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                placeholder="Acme Inc"
                required
              />
            </div>
            <div className="form-group">
              <label>Required Skills *</label>
              <input
                value={form.required_skills}
                onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
                placeholder="Python, React, SQL, AWS"
                required
              />
            </div>
            <div className="form-group">
              <label>Experience Required</label>
              <input
                value={form.experience_required}
                onChange={(e) => setForm({ ...form, experience_required: e.target.value })}
                placeholder="e.g. 3+ years"
              />
            </div>
            <div className="form-group">
              <label>Job Description *</label>
              <textarea
                value={form.job_description}
                onChange={(e) => setForm({ ...form, job_description: e.target.value })}
                placeholder="Describe the role, responsibilities, and requirements..."
                rows={6}
                required
              />
            </div>
            <div className="form-group">
              <label>Number of Openings</label>
              <input
                type="number"
                min={1}
                value={form.number_of_openings}
                onChange={(e) => setForm({ ...form, number_of_openings: parseInt(e.target.value) || 1 })}
              />
            </div>
            {error && <p className="error">{error}</p>}
            <div className="form-actions">
              <button type="button" className="btn btn-ghost" onClick={() => navigate('/recruiter')}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Creating...' : 'Create Job'}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
