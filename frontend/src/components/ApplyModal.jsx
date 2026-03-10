import { useState } from 'react';
import { applyForJob } from '../api';

export default function ApplyModal({ job, onClose, onSuccess }) {
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const [form, setForm] = useState({
    name: profile.name || '',
    email: profile.email || '',
    phone: profile.phone || '',
    skills: profile.skills || '',
    education: profile.education || '',
    experience: profile.experience || '',
  });
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('job_id', job.id);
      formData.append('name', form.name);
      formData.append('email', form.email);
      formData.append('phone', form.phone);
      formData.append('skills', form.skills);
      formData.append('education', form.education);
      formData.append('experience', form.experience);
      if (resume) formData.append('resume', resume);
      await applyForJob(formData);
      onSuccess();
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Apply for {job.job_title}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name *</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Skills</label>
            <textarea value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} rows={2} placeholder="Python, React, SQL..." />
          </div>
          <div className="form-group">
            <label>Education</label>
            <textarea value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })} rows={2} placeholder="B.Tech Computer Science, 2020" />
          </div>
          <div className="form-group">
            <label>Experience</label>
            <textarea value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} rows={2} placeholder="2+ years as Software Engineer" />
          </div>
          <div className="form-group">
            <label>Resume (PDF/DOCX) *</label>
            <input type="file" accept=".pdf,.docx,.doc" onChange={(e) => setResume(e.target.files?.[0])} required />
          </div>
          {error && <p className="error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Submitting...' : 'Submit Application'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
