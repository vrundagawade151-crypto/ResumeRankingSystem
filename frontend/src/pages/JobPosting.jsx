import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../api';
import './JobPosting.css';

export default function JobPosting() {
  const navigate = useNavigate();
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const [form, setForm] = useState({
    job_title: '',
    company_name: profile.company_name || '',
    required_skills: '',
    experience_required: 'mid-level',
    job_description: '',
    number_of_openings: 1,
    location: '',
    job_type: 'full-time',
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
      const message = err.response?.data?.message || err.response?.data?.error || 'Failed to create job';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-posting-page">
      <div className="container page-content">
        <h1>Post a New Job</h1>
        <div className="form-card card">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
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
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Location</label>
                <input
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="e.g. New York, NY"
                />
              </div>
              <div className="form-group">
                <label>Job Type</label>
                <select
                  value={form.job_type}
                  onChange={(e) => setForm({ ...form, job_type: e.target.value })}
                >
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                  <option value="freelance">Freelance</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Experience Required</label>
                <select
                  value={form.experience_required}
                  onChange={(e) => setForm({ ...form, experience_required: e.target.value })}
                >
                  <option value="entry-level">Entry-level</option>
                  <option value="mid-level">Mid-level</option>
                  <option value="senior-level">Senior-level</option>
                  <option value="lead-principal">Lead/Principal</option>
                </select>
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
              <label>Job Description *</label>
              <textarea
                value={form.job_description}
                onChange={(e) => setForm({ ...form, job_description: e.target.value })}
                placeholder="Describe the role, responsibilities, and requirements..."
                rows={6}
                required
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
