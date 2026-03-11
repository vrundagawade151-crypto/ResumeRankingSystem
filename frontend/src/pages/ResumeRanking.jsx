import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getJob, getApplicants, extractAndRankResumes, getRankedCandidates } from '../api';
import Navbar from '../components/Navbar';
import './ResumeRanking.css';

export default function ResumeRanking() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [ranked, setRanked] = useState([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [limit, setLimit] = useState(50);
  const [fileType, setFileType] = useState('all');

  const loadData = () => {
    setLoading(true);
    Promise.all([
      getJob(jobId).then((r) => r.data.job),
      getApplicants(jobId).then((r) => r.data.applicants || []),
      getRankedCandidates(jobId).then((r) => r.data.ranked_candidates || []).catch(() => []),
    ])
      .then(([j, a, r]) => {
        setJob(j);
        setApplicants(a);
        setRanked(r);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [jobId]);

  const handleExtract = async () => {
    setExtracting(true);
    try {
      const res = await extractAndRankResumes(jobId, limit, fileType);
      setRanked(res.data.ranked_candidates || []);
    } catch (err) {
      alert(err.response?.data?.error || 'Extraction failed');
    } finally {
      setExtracting(false);
    }
  };

  const displayList = ranked.length > 0 ? ranked : applicants.map((a) => ({ ...a, ranking_score: null }));

  return (
    <div className="resume-ranking-page">
      <Navbar user={JSON.parse(localStorage.getItem('user'))} role="recruiter" />
      <div className="container page-content">
        <Link to={`/recruiter/jobs/${jobId}/applicants`} className="back-link">← Back to Applicants</Link>
        <h1>AI Resume Screening</h1>
        <p className="subtitle">{job?.job_title} — {job?.company_name}</p>

        <div className="ranking-controls card">
          <h3>Extract & Rank Resumes</h3>
          <p>Total applicants: <strong>{applicants.length}</strong> (with resume: {applicants.filter((a) => a.resume_path).length})</p>
          <div className="controls-row">
            <div className="form-group">
              <label>Process limit</label>
              <input type="number" min={1} value={limit} onChange={(e) => setLimit(parseInt(e.target.value) || 50)} />
            </div>
            <div className="form-group">
              <label>File type</label>
              <select value={fileType} onChange={(e) => setFileType(e.target.value)}>
                <option value="all">All (PDF + Word)</option>
                <option value="pdf">PDF only</option>
                <option value="docx">Word only</option>
              </select>
            </div>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleExtract}
              disabled={extracting || applicants.filter((a) => a.resume_path).length === 0}
            >
              {extracting ? 'Processing...' : '🤖 Extract Resume'}
            </button>
          </div>
          <p className="hint">Uses NLP to extract skills, education, experience. Ranks by 60% skill + 20% experience + 20% education match.</p>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <div className="ranked-list">
            <h2>Ranked Candidates</h2>
            {displayList.length === 0 ? (
              <p className="empty-state">No applicants to rank.</p>
            ) : (
              <div className="ranked-cards">
                {displayList.map((c, i) => (
                  <div key={c.id || i} className="ranked-card card">
                    <div className="rank-badge">
                      #{i + 1} {c.ranking_score != null && (
                        <span className="score">Score: {typeof c.ranking_score === 'number' ? c.ranking_score.toFixed(1) : c.ranking_score}%</span>
                      )}
                    </div>
                    <h4>{c.name || c.extracted_name}</h4>
                    <p className="email">{c.email}</p>
                    {(c.extracted_skills || c.skills) && (
                      <p><strong>Skills:</strong> {c.extracted_skills || c.skills}</p>
                    )}
                    {(c.resume_extraction || (c.skill_match_score != null)) && (
                      <div className="score-breakdown">
                        <span>Skill: {c.resume_extraction?.skill_match_score ?? c.skill_match_score ?? '-'}%</span>
                        <span>Exp: {c.resume_extraction?.experience_match_score ?? c.experience_match_score ?? '-'}%</span>
                        <span>Edu: {c.resume_extraction?.education_match_score ?? c.education_match_score ?? '-'}%</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
