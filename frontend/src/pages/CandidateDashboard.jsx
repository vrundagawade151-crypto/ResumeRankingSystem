import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getJobs, getMyApplications, uploadCandidateResume } from '../api';
import api from '../api';
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
  const [applicationFilter, setApplicationFilter] = useState('all');

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
      // Handle both backend 'title'/'company'/'requirements' and any frontend alternative names
      const title = (job.job_title || job.title || '').toLowerCase();
      const company = (job.company_name || job.company || '').toLowerCase();
      const skills = (job.required_skills || job.requirements || '').toLowerCase();
      
      const matchesSearch = !search || 
        title.includes(searchLower) || 
        company.includes(searchLower) || 
        skills.includes(searchLower);
        
      const matchesLocation = !locationFilter ||
        (job.location || '').toLowerCase().includes(locationFilter.toLowerCase());
        
      const matchesExperience = !experienceFilter ||
        (job.experience_required || '').toLowerCase().includes(experienceFilter.toLowerCase());
        
      const matchesJobType = !jobTypeFilter || jobTypeFilter === 'all' ||
        (job.job_type || '').toLowerCase().includes(jobTypeFilter.toLowerCase());
        
      return matchesSearch && matchesLocation && matchesExperience && matchesJobType;
    });
  }, [jobs, search, locationFilter, experienceFilter, jobTypeFilter]);

  const filteredApplications = useMemo(() => {
    let result = applications.filter((app) => {
      const status = (app.status || 'pending').toLowerCase();
      
      // Status filtering
      if (applicationFilter === 'under_review' && !['pending', 'reviewed'].includes(status)) return false;
      if (applicationFilter === 'shortlisted' && !['accepted', 'shortlisted', 'interview'].includes(status)) return false;
      if (applicationFilter === 'rejected' && status !== 'rejected') return false;

      // Search filtering
      if (applicationSearch) {
        const searchLower = applicationSearch.toLowerCase();
        const job = jobs.find((j) => j.id === app.job_id);
        const title = (job?.job_title || job?.title || app.job_title || '').toLowerCase();
        const company = (job?.company_name || job?.company || app.company_name || '').toLowerCase();
        if (!title.includes(searchLower) && !company.includes(searchLower)) return false;
      }
      return true;
    });

    // Sort by date
    result.sort((a, b) => {
      const dateA = new Date(a.applied_at || a.created_at || a.date_applied || 0);
      const dateB = new Date(b.applied_at || b.created_at || b.date_applied || 0);
      return applicationSort === 'newest' ? dateB - dateA : dateA - dateB;
    });

    return result;
  }, [applications, applicationFilter, applicationSearch, applicationSort, jobs]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const handleWithdraw = async (appId) => {
    if (window.confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) {
      try {
        await api.put(`/applications/${appId}`, { status: 'withdrawn' });
        // Refresh apps
        const res = await getMyApplications();
        setApplications(Array.isArray(res.data) ? res.data : (res.data?.applications || []));
      } catch (err) {
        alert('Failed to withdraw application');
      }
    }
  };

  const [uploadingResume, setUploadingResume] = useState(false);

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingResume(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);
      const res = await uploadCandidateResume(formData);

      const updatedProfile = {
        ...profile,
        skills: res.data.extracted_details.skills,
        experience: res.data.extracted_details.experience,
        education: res.data.extracted_details.education,
      };

      localStorage.setItem('profile', JSON.stringify(updatedProfile));
      alert('Resume uploaded & Profile details updated automatically!');
      window.location.reload();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to upload resume');
    } finally {
      setUploadingResume(false);
      e.target.value = null; // reset input
    }
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
                <button type="button" className={`filter-tab ${applicationFilter === 'all' ? 'active' : ''}`} onClick={() => setApplicationFilter('all')}>All Applications</button>
                <button type="button" className={`filter-tab ${applicationFilter === 'under_review' ? 'active' : ''}`} onClick={() => setApplicationFilter('under_review')}>Under Review</button>
                <button type="button" className={`filter-tab ${applicationFilter === 'shortlisted' ? 'active' : ''}`} onClick={() => setApplicationFilter('shortlisted')}>Shortlisted</button>
                <button type="button" className={`filter-tab ${applicationFilter === 'rejected' ? 'active' : ''}`} onClick={() => setApplicationFilter('rejected')}>Rejected</button>
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
            {filteredApplications.length === 0 ? (
              <div className="jobs-empty card">
                <p>No applications found matching your criteria.</p>
                <button type="button" className="btn btn-primary" onClick={() => {
                  if (applications.length === 0) setActiveTab('jobs');
                  else { setApplicationFilter('all'); setApplicationSearch(''); }
                }}>
                  {applications.length === 0 ? 'Browse Jobs' : 'Clear Filters'}
                </button>
              </div>
            ) : (
              <div className="applications-list">
                {filteredApplications.map((app) => {
                  const job = jobs.find((j) => j.id === app.job_id);
                  const rawStatus = (app.status || 'pending').toLowerCase();
                  let displayStatus = 'Applied';
                  let statusClass = 'status-applied';
                  
                  if (rawStatus === 'pending') { displayStatus = 'Applied'; statusClass = 'status-applied'; }
                  if (rawStatus === 'reviewed') { displayStatus = 'Under Review'; statusClass = 'status-under-review'; }
                  if (rawStatus === 'shortlisted' || rawStatus === 'accepted') { displayStatus = 'Shortlisted'; statusClass = 'status-shortlisted'; }
                  if (rawStatus === 'interview') { displayStatus = 'Interview'; statusClass = 'status-interview'; }
                  if (rawStatus === 'rejected') { displayStatus = 'Rejected'; statusClass = 'status-rejected'; }
                  if (rawStatus === 'offer' || rawStatus === 'offer_received') { displayStatus = 'Offer'; statusClass = 'status-offer'; }
                  if (rawStatus === 'withdrawn') { displayStatus = 'Withdrawn'; statusClass = 'status-applied'; }

                  const appliedDate = app.date_applied || app.applied_date || app.created_at || app.applied_at || 'Apr 20, 2025';
                  const resumeName = app.resume_path ? app.resume_path.split(/[\\/]/).pop() : 'resume.pdf';
                  const isWithdrawable = !(displayStatus === 'Rejected' || displayStatus === 'Offer' || displayStatus === 'Withdrawn');

                  return (
                    <div key={app.id} className="application-card card">
                      <div className="application-main" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div>
                            <h3>{job?.job_title || job?.title || app.job_title || 'Job Title'}</h3>
                            <span className="job-company" style={{ color: '#475569', fontWeight: 500, margin: '4px 0 0 0', fontSize: '14px' }}>
                              {job?.company_name || job?.company || app.company_name || 'Company'} • {job?.location || 'Location'} • {job?.job_type || 'Job Type'}
                            </span>
                          </div>
                          <span className={`status-badge ${statusClass}`} style={{ marginLeft: '12px' }}>
                            {displayStatus}
                          </span>
                        </div>
                        
                        <div style={{ marginTop: '16px', padding: '14px', background: '#f8fafc', borderRadius: '10px', fontSize: '13px', color: '#475569', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #e2e8f0' }}>
                          <div>
                            <div><strong>Date Applied:</strong> {appliedDate.substring(0, 10)}</div>
                            <div style={{ marginTop: '6px' }}><strong>Resume:</strong> {resumeName.replace('app_', '')}</div>
                          </div>
                          {app.ai_score ? (
                            <div style={{ textAlign: 'right' }}>
                              <span style={{ fontSize: '18px', fontWeight: 700, color: '#4f46e5' }}>{app.ai_score}%</span>
                              <div style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Match Score</div>
                            </div>
                          ) : null}
                        </div>

                        <div className="application-actions" style={{ display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
                          <button type="button" className="btn btn-primary" style={{ flex: 1, minWidth: '100%', marginBottom: '4px' }}>View Details</button>
                          <div style={{ display: 'flex', gap: '8px', width: '100%' }}>
                            <button type="button" className="btn btn-ghost" style={{ flex: 1, fontSize: '13px', padding: '8px 12px' }}>Edit</button>
                            <button type="button" className="btn btn-ghost" style={{ flex: 1, fontSize: '13px', padding: '8px 12px' }} onClick={() => app.resume_path && window.open('/api/applications/resume/' + encodeURIComponent(app.resume_path), '_blank')}>Resume</button>
                            <button type="button" className="btn btn-ghost" style={{ flex: 1, fontSize: '13px', padding: '8px 12px', color: isWithdrawable ? '#dc2626' : '#cbd5e1', borderColor: isWithdrawable ? 'rgba(220, 38, 38, 0.2)' : '#e2e8f0' }} disabled={!isWithdrawable} onClick={() => handleWithdraw(app.id)}>Withdraw</button>
                          </div>
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
                <input
                  type="file"
                  id="resume-upload"
                  style={{ display: 'none' }}
                  accept=".pdf,.doc,.docx"
                  onChange={handleResumeUpload}
                />
                <button type="button" className="btn btn-primary" onClick={() => document.getElementById('resume-upload').click()} disabled={uploadingResume}>
                  {uploadingResume ? 'Uploading...' : 'Upload Resume'}
                </button>
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
