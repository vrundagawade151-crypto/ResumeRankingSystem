import { useState } from 'react';
import { applyForJob } from '../api';

export default function ApplyModal({ job, onClose, onSuccess }) {
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const [form, setForm] = useState({
    name: user.name || profile.name || '',
    email: user.email || profile.email || '',
    phone: profile.phone || '',
    background: 'technical',
    experience: profile.experience || '',
    location: profile.location || '',
  });
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('job_id', job.id);
      if (user.id) formData.append('user_id', user.id);
      formData.append('name', form.name);
      formData.append('email', form.email);
      formData.append('phone', form.phone);
      formData.append('background', form.background);
      formData.append('experience', form.experience);
      formData.append('location', form.location);
      if (resume) formData.append('resume', resume);
      await applyForJob(formData);
      setSuccess(true);
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
          <h2>{success ? 'Success!' : `Apply for ${job.job_title}`}</h2>
          <button className="modal-close" onClick={() => {
            if (success) {
              onSuccess();
              window.location.reload();
            } else {
              onClose();
            }
          }}>×</button>
        </div>
        
        {success ? (
          <div className="success-message" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem', color: 'var(--success, #22c55e)' }}>✓</div>
            <h3>Application Submitted Successfully!</h3>
            <p style={{ marginTop: '0.5rem', color: 'var(--text-light)' }}>
              Your application for {job.job_title} has been successfully submitted and is under review.
            </p>
            <button 
              type="button" 
              className="btn btn-primary" 
              style={{ marginTop: '1.5rem', minWidth: '120px' }} 
              onClick={() => {
                onSuccess();
                window.location.reload();
              }}
            >
              OK
            </button>
          </div>
        ) : (
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
            <label>Background</label>
            <select value={form.background} onChange={(e) => setForm({ ...form, background: e.target.value })}>
              <option value="technical">Technical</option>
              <option value="non-technical">Non-Technical</option>
            </select>
          </div>
          <div className="form-group">
            <label>Work Experience</label>
            <textarea value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} rows={2} placeholder="2+ years as Software Engineer" />
          </div>
          <div className="form-group">
            <label>Location</label>
            <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="City, State" />
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
        )}
      </div>
    </div>
  );
}
