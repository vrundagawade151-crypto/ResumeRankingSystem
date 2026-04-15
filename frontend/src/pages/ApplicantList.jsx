import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getApplicants, getJob, updateApplicationStatus } from '../api';
import './ApplicantList.css';

export default function ApplicantList() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [applicants, setApplicants] = useState([]);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, [jobId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [appRes, jobRes] = await Promise.all([
        getApplicants(jobId),
        getJob(jobId),
      ]);
      setApplicants(Array.isArray(appRes.data) ? appRes.data : (appRes.data?.applications || []));
      setJob(jobRes.data?.job || jobRes.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load applicants');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (applicationId, newStatus) => {
    try {
      await updateApplicationStatus(applicationId, newStatus);
      setApplicants((prev) =>
        prev.map((app) =>
          app.id === applicationId ? { ...app, status: newStatus } : app
        )
      );
    } catch (err) {
      console.error('Failed to update status', err);
      alert('Failed to update status');
    }
  };

  const downloadResume = (resumePath) => {
    if (resumePath) {
      window.open('/api/applications/resume/' + encodeURIComponent(resumePath), '_blank');
    }
  };

  if (loading) {
    return (
      <div className="applicant-list-page">
        <div className="loading-state">
          <p>Loading applicants...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="applicant-list-page">
      <div className="page-header">
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/recruiter')}>← Back</button>
        <div className="header-title">
          <h1>{job?.title || job?.job_title || 'Applicants'}</h1>
          <p className="subtitle">{job?.company || job?.company_name} — {applicants.length} applicant(s)</p>
        </div>
      </div>

      {error && (
        <div className="error-state card">
          <p>⚠️ {error}</p>
        </div>
      )}

      {applicants.length === 0 ? (
        <div className="empty-state card">
          <p>📭 No applicants yet</p>
          <p className="text-muted">When candidates apply, they'll appear here</p>
        </div>
      ) : (
        <div className="applicants-table-container card">
          <table className="applicants-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Applied On</th>
                <th>Resume</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {applicants.map((applicant) => (
                <tr key={applicant.id} className={`status-${applicant.status || 'pending'}`}>
                  <td className="applicant-name">
                    <strong>{applicant.applicant_name || applicant.candidate_name || 'Candidate'}</strong>
                  </td>
                  <td className="applicant-email">{applicant.applicant_email || applicant.email}</td>
                  <td>
                    <span className={`status-badge ${applicant.status || 'pending'}`}>
                      {(applicant.status || 'pending').charAt(0).toUpperCase() + (applicant.status || 'pending').slice(1)}
                    </span>
                  </td>
                  <td className="applied-date">
                    {applicant.applied_at || applicant.created_at ? new Date(applicant.applied_at || applicant.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td>
                    {applicant.resume_path ? (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => downloadResume(applicant.resume_path)}
                      >
                        📥 Download
                      </button>
                    ) : (
                      <span className="text-muted">No resume</span>
                    )}
                  </td>
                  <td>
                    <select
                      className="status-select"
                      value={applicant.status || 'pending'}
                      onChange={(e) => handleStatusChange(applicant.id, e.target.value)}
                    >
                      <option value="pending">Pending</option>
                      <option value="reviewed">Reviewed</option>
                      <option value="accepted">Accepted</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
