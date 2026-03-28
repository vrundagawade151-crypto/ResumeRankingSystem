import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getJobs, getMyApplications } from '../api';
import ApplyModal from '../components/ApplyModal';
import './CandidateDashboard.css';

export default function CandidateDashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applyJob, setApplyJob] = useState(null);
  const [detailJob, setDetailJob] = useState(null);
  const [activeTab, setActiveTab] = useState('jobs');

  const [search, setSearch] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [experienceFilter, setExperienceFilter] = useState('');
  const [jobTypeFilter, setJobTypeFilter] = useState('');

  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const profileSkills = Array.isArray(profile.skills)
    ? profile.skills
    : (profile.skills || 'Python, Java, SQL, React, AWS').split(',').map((s) => s.trim()).filter(Boolean);
  const profileExperience = Array.isArray(profile.experience) ? profile.experience : [
    {
      title: 'Software Engineer',
      company: 'Tech Innovate Inc.',
      duration: '2022 - Present',
      location: 'San Francisco, CA',
      description: 'Built scalable hiring workflows and optimized data pipelines for candidate scoring.',
    },
    {
      title: 'UI/UX Designer',
      company: 'Creative Solutions',
      duration: '2020 - 2022',
      location: 'New York, NY',
      description: 'Collaborated with cross-functional teams to improve application experience and conversion.',
    },
  ];
  const profileEducation = Array.isArray(profile.education) ? profile.education : [
    {
      degree: 'B.S. Computer Science',
      university: 'University of California, Berkeley',
      year: '2018',
    },
  ];
  const profileCompleteness = profile.completeness || 85;

  const [applicationSearch, setApplicationSearch] = useState('');
  const [applicationSort, setApplicationSort] = useState('newest');

  useEffect(() => {
    getJobs()
      .then((res) => setJobs(res.data.jobs || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (activeTab === 'applications') {
      getMyApplications()
        .then((res) => setApplications(Array.isArray(res.data) ? res.data : (res.data?.applications || [])))
        .catch(() => setApplications([]));
    }
  }, [activeTab]);

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const searchLower = search.toLowerCase();
      const matchesSearch = !search || 
        (job.job_title || '').toLowerCase().includes(searchLower) ||
        (job.company_name || '').toLowerCase().includes(searchLower) ||
        (job.required_skills || '').toLowerCase().includes(searchLower);
      const matchesLocation = !locationFilter || 
        (job.company_name || '').toLowerCase().includes(locationFilter.toLowerCase());
      const matchesExperience = !experienceFilter || 
        (job.experience_required || '').toLowerCase().includes(experienceFilter.toLowerCase());
      const matchesJobType = !jobTypeFilter || jobTypeFilter === 'all' ||
        (job.job_description || job.job_title || '').toLowerCase().includes(jobTypeFilter.toLowerCase());
      return matchesSearch && matchesLocation && matchesExperience && matchesJobType;
    });
  }, [jobs, search, locationFilter, experienceFilter, jobTypeFilter]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <div className="candidate-dashboard">
      <header className="candidate-nav">
        <div className="candidate-nav-inner">
          <Link to="/" className="candidate-logo">
            <span className="logo-icon">📋</span>
            <span>AI ResumeScreen</span>
          </Link>
          <nav className="candidate-nav-links">
            <button
              type="button"
              className={`nav-tab ${activeTab === 'jobs' ? 'active' : ''}`}
              onClick={() => setActiveTab('jobs')}
            >
              Jobs
            </button>
            <button
              type="button"
              className={`nav-tab ${activeTab === 'applications' ? 'active' : ''}`}
              onClick={() => setActiveTab('applications')}
            >
              My Applications
            </button>
            <button
              type="button"
              className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              Profile
            </button>
          </nav>
        </div>
      </header>

      <main className="candidate-main">
        {activeTab === 'jobs' && (
          <>
            <section className="search-section">
              <div className="search-bar-row">
                <div className="search-input-wrap">
                  <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="search"
                    placeholder="Search for jobs, skills, companies"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="search-input"
                  />
                </div>
                <select
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="">Location</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                </select>
                <select
                  value={experienceFilter}
                  onChange={(e) => setExperienceFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="">Experience Level</option>
                  <option value="fresher">Fresher</option>
                  <option value="1">1+ years</option>
                  <option value="2">2+ years</option>
                  <option value="3">3+ years</option>
                  <option value="5">5+ years</option>
                </select>
                <select
                  value={jobTypeFilter}
                  onChange={(e) => setJobTypeFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">Job Type</option>
                  <option value="full-time">Full-time</option>
                  <option value="internship">Internship</option>
                  <option value="remote">Remote</option>
                </select>
                <button type="button" className="btn-search" onClick={() => document.getElementById('job-listings')?.scrollIntoView({ behavior: 'smooth' })}>
                  Search
                </button>
              </div>
            </section>

            <section className="jobs-section" id="job-listings">
              <div className="section-header">
                <h2>Job Listings</h2>
                <span className="results-count">{filteredJobs.length} jobs</span>
              </div>
              {loading ? (
                <div className="jobs-loading">Loading jobs...</div>
              ) : filteredJobs.length === 0 ? (
                <div className="jobs-empty card">
                  <p>No jobs found. Try adjusting your search or filters.</p>
                </div>
              ) : (
                <div className="jobs-grid">
                  {filteredJobs.map((job) => (
                    <div key={job.id} className="job-card card">
                      <div className="job-card-header">
                        <div className="job-icon-wrap">
                          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div>
                          <h3>{job.job_title || job.title}</h3>
                          <span className="job-company">{job.company_name || job.company}</span>
                        </div>
                      </div>
                      <div className="job-card-skills">
                        {(job.required_skills || job.requirements || '')
                          .split(',')
                          .map((s) => s.trim())
                          .filter(Boolean)
                          .slice(0, 3)
                          .map((s, i) => (
                            <span key={i} className="skill-tag">{s}</span>
                          ))}
                      </div>
                      <div className="job-card-meta">
                        <span className="meta-item">
                          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          {job.experience_required || 'Not specified'}
                        </span>
                      </div>
                      <p className="job-card-desc">{(job.job_description || job.description || '').slice(0, 100)}...</p>
                      <div className="job-card-actions">
                        <button
                          type="button"
                          className="btn btn-apply"
                          onClick={() => setApplyJob(job)}
                        >
                          Apply
                        </button>
                        <button
                          type="button"
                          className="btn btn-view-details"
                          onClick={() => setDetailJob(job)}
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        {activeTab === 'applications' && (
          <section className="applications-section">
            <div className="applications-header">
              <div>
                <h2>My Applications</h2>
                <p>Track the status of your job applications in one place.</p>
              </div>
            </div>

            <div className="applications-filters card">
              <div className="filter-tabs">
                <button type="button" className="filter-tab active">All Applications</button>
                <button type="button" className="filter-tab">Under Review</button>
                <button type="button" className="filter-tab">Interview</button>
                <button type="button" className="filter-tab">Rejected</button>
              </div>
              <div className="applications-search-row">
                <div className="search-input-wrap">
                  <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="search"
                    placeholder="Search applications..."
                    value={applicationSearch}
                    onChange={(e) => setApplicationSearch(e.target.value)}
                    className="search-input"
                  />
                </div>
                <select
                  className="filter-select"
                  value={applicationSort}
                  onChange={(e) => setApplicationSort(e.target.value)}
                >
                  <option value="newest">Newest</option>
                  <option value="oldest">Oldest</option>
                </select>
              </div>
            </div>
            {applications.length === 0 ? (
              <div className="jobs-empty card">
                <p>You haven&apos;t applied to any jobs yet.</p>
                <button type="button" className="btn btn-primary" onClick={() => setActiveTab('jobs')}>
                  Browse Jobs
                </button>
              </div>
            ) : (
              <div className="applications-list">
                {applications.map((app) => {
                  const job = jobs.find((j) => j.id === app.job_id);
                  const skills = (job?.required_skills || app.skills || 'Python, SQL, React')
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean)
                    .slice(0, 4);
                  const status = (app.status || 'under review').toLowerCase();
                  const appliedDate = app.date_applied || app.applied_date || app.created_at || 'Apr 20, 2025';
                  return (
                    <div key={app.id} className="application-card card">
                      <div className="application-main">
                        <div>
                          <h3>{job?.job_title || app.job_title || 'Job'}</h3>
                          <span className="job-company">{job?.company_name || app.company_name || '-'}</span>
                          <div className="application-skills">
                            {skills.map((skill) => (
                              <span key={skill} className="skill-tag">{skill}</span>
                            ))}
                          </div>
                        </div>
                        <div className="application-meta">
                          <span className="application-date">Date Applied: {appliedDate}</span>
                          <span className={`status-badge status-${status.replace(/\s+/g, '-')}`}>
                            {app.status || 'Under Review'}
                          </span>
                          <button type="button" className="btn btn-view-details">View Details</button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {activeTab === 'profile' && (
          <section className="profile-section">
            <div className="profile-header card">
              <div className="profile-summary">
                <div className="profile-photo">
                  {(profile.name || user?.name || 'Candidate').charAt(0).toUpperCase()}
                </div>
                <div className="profile-summary-text">
                  <h2>{profile.name || user?.name || 'Candidate Name'}</h2>
                  <p className="profile-role">{profile.title || 'Software Engineer'}</p>
                  <div className="profile-contact">
                    <span>{profile.location || 'San Francisco, CA'}</span>
                    <span>{profile.email || user?.email || 'candidate@email.com'}</span>
                    <span>{profile.phone || '+1 (555) 123-4567'}</span>
                  </div>
                </div>
              </div>
              <div className="profile-actions">
                <button type="button" className="btn btn-primary">Upload Resume</button>
                <button type="button" className="icon-btn" aria-label="Edit Profile">
                  <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536M9 11l6 6M3 21h6l12-12a2.5 2.5 0 00-3.536-3.536L5.5 17.5 3 21z" />
                  </svg>
                </button>
                <button type="button" className="btn btn-ghost" onClick={handleLogout}>Logout</button>
              </div>
            </div>

            <div className="profile-grid">
              <div className="profile-card card">
                <div className="card-header">
                  <h3>Skills</h3>
                  <button type="button" className="link-btn">Add Skills</button>
                </div>
                <div className="skills-grid">
                  {profileSkills.map((skill) => (
                    <span key={skill} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>

              <div className="profile-card card">
                <div className="card-header">
                  <h3>Work Experience</h3>
                </div>
                <div className="experience-list">
                  {profileExperience.map((exp, idx) => (
                    <div key={`${exp.title}-${idx}`} className="experience-item">
                      <div className="experience-title">{exp.title}</div>
                      <div className="experience-company">{exp.company}</div>
                      <div className="experience-meta">{exp.duration} · {exp.location}</div>
                      <p>{exp.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="profile-card card">
                <div className="card-header">
                  <h3>Education</h3>
                </div>
                <div className="education-list">
                  {profileEducation.map((edu, idx) => (
                    <div key={`${edu.degree}-${idx}`} className="education-item">
                      <div className="education-degree">{edu.degree}</div>
                      <div className="education-school">{edu.university}</div>
                      <div className="education-year">{edu.year}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="profile-card card">
                <div className="card-header">
                  <h3>Resume Status</h3>
                </div>
                <div className="resume-status">
                  <div className="resume-progress">
                    <div className="progress-label">Resume completeness: {profileCompleteness}%</div>
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: `${profileCompleteness}%` }} />
                    </div>
                  </div>
                  <div className="visibility-toggle">
                    <span>Profile visibility</span>
                    <button type="button" className="toggle-pill">Public</button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {applyJob && (
        <ApplyModal
          job={applyJob}
          onClose={() => setApplyJob(null)}
          onSuccess={() => setApplyJob(null)}
        />
      )}

      {detailJob && (
        <div className="modal-overlay" onClick={() => setDetailJob(null)}>
          <div className="modal-content card job-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{detailJob.job_title || detailJob.title}</h2>
              <button type="button" className="modal-close" onClick={() => setDetailJob(null)}>×</button>
            </div>
            <p className="detail-company">{detailJob.company_name || detailJob.company}</p>
            <div className="detail-meta">
              <span>Skills: {detailJob.required_skills || detailJob.requirements || '-'}</span>
              <span>Experience: {detailJob.experience_required || 'Not specified'}</span>
            </div>
            <div className="detail-description">
              <h4>Description</h4>
              <p>{detailJob.job_description || detailJob.description || '-'}</p>
            </div>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setDetailJob(null);
                setApplyJob(detailJob);
              }}
            >
              Apply Now
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
