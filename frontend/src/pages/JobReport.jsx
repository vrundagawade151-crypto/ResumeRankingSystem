import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getRecruiterReport } from '../api';

export default function JobReport() {
  const { jobId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getRecruiterReport(jobId)
      .then((res) => {
        setReport(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError('Failed to load report');
        setLoading(false);
      });
  }, [jobId]);

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading report...</div>;
  if (error) return <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>{error}</div>;
  if (!report) return <div style={{ padding: '2rem', textAlign: 'center' }}>No data available</div>;

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Job Report: {report.job_title}</h1>
        <Link to="/recruiter" className="btn btn-ghost">Back to Dashboard</Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{report.total_applications}</div>
          <div style={{ color: 'var(--text-light)' }}>Total Applications</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{report.pending}</div>
          <div style={{ color: 'var(--text-light)' }}>Pending</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{report.accepted}</div>
          <div style={{ color: 'var(--text-light)' }}>Accepted</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{report.average_score || 0}%</div>
          <div style={{ color: 'var(--text-light)' }}>Average Score</div>
        </div>
      </div>

      <div className="card">
        <h2 style={{ padding: '1rem', borderBottom: '1px solid var(--border)' }}>Candidates</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'var(--bg-secondary)' }}>
              <th style={{ padding: '1rem', textAlign: 'left' }}>#</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Email</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Domain</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Experience</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Score</th>
              <th style={{ padding: '1rem', textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {report.candidates.map((candidate, index) => (
              <tr key={candidate.application_id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '1rem' }}>{index + 1}</td>
                <td style={{ padding: '1rem' }}>
                  {candidate.name_mismatch ? (
                    <span style={{ color: 'red' }}>{candidate.applicant_name} (Rejected)</span>
                  ) : (
                    candidate.applicant_name
                  )}
                </td>
                <td style={{ padding: '1rem' }}>{candidate.applicant_email}</td>
                <td style={{ padding: '1rem' }}>{candidate.domain || '-'}</td>
                <td style={{ padding: '1rem' }}>{candidate.experience_years || 0} years</td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '4px',
                    background: candidate.score >= 70 ? 'var(--success)' : candidate.score >= 50 ? 'var(--warning)' : 'var(--error)',
                    color: 'white'
                  }}>
                    {candidate.score || 0}%
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span className={`badge badge-${candidate.status}`}>{candidate.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {report.candidates.some(c => c.extracted_certifications) && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h2 style={{ padding: '1rem', borderBottom: '1px solid var(--border)' }}>Certifications Found</h2>
          {report.candidates.filter(c => c.extracted_certifications).map(candidate => (
            <div key={candidate.application_id} style={{ padding: '1rem', borderBottom: '1px solid var(--border)' }}>
              <strong>{candidate.applicant_name}</strong>
              <p style={{ marginTop: '0.5rem', color: 'var(--text-light)' }}>{candidate.extracted_certifications}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}