import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api, { getApplicants, getJob } from '../api';
import Navbar from '../components/Navbar';
import './ApplicantList.css';

export default function ApplicantList() {
  const { jobId } = useParams();
  const [applicants, setApplicants] = useState([]);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getApplicants(jobId).then((r) => r.data),
      getJob(jobId).then((r) => r.data),
    ])
      .then(([appData, jobData]) => {
        setApplicants(appData.applicants || []);
        setJob(jobData.job);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [jobId]);

  const downloadResume = async (path) => {
    if (!path) return;
    try {
      const res = await api.get(`/applications/resume/${path}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = path.split('_').pop() || 'resume.pdf';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('Failed to download');
    }
  };

  return (
    <div className="applicant-list-page">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="recruiter" />
      <div className="container page-content">
        <Link to="/recruiter" className="back-link">← Back to Jobs</Link>
        <h1>{job?.job_title || 'Applicants'}</h1>
        <p className="subtitle">{job?.company_name} — {applicants.length} applicant(s)</p>

        <div className="applicant-actions">
          <Link to={`/recruiter/jobs/${jobId}/ranking`} className="btn btn-primary">
            🤖 Extract & Rank Resumes (AI)
          </Link>
        </div>

        {loading ? (
          <p>Loading applicants...</p>
        ) : applicants.length === 0 ? (
          <p className="empty-state">No applicants yet.</p>
        ) : (
          <div className="applicants-table-wrap card">
            <table className="applicants-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Skills</th>
                  <th>Resume</th>
                </tr>
              </thead>
              <tbody>
                {applicants.map((app, i) => (
                  <tr key={app.id}>
                    <td>{app.id}</td>
                    <td>{app.name}</td>
                    <td>{app.email}</td>
                    <td className="skills-cell">{app.skills || '-'}</td>
                    <td>
                      {app.resume_path ? (
                        <button type="button" className="btn btn-ghost btn-sm" onClick={() => downloadResume(app.resume_path)}>
                          Download
                        </button>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
