import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './Landing.css';

export default function Landing() {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const role = localStorage.getItem('role');

  return (
    <div className="landing">
      <Navbar user={user} role={role} />

      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-copy">
            <h1>AI-Based Resume Screening &amp; Ranking System</h1>
            <p>Find the best candidates fast with AI-powered screening.</p>
            <div className="hero-actions">
              <Link to="/role-selection" className="btn btn-primary btn-lg">Get Started</Link>
              <Link to="/login?role=candidate" className="btn btn-accent btn-lg">Login as Candidate</Link>
              <Link to="/login?role=recruiter" className="btn btn-outline btn-lg">Login as Recruiter</Link>
            </div>
          </div>
          <div className="hero-visual">
            <img className="hero-image" src="/assets/resume-screening-hero.svg" alt="Resume screening workspace" />
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container cta-grid">
          <div className="cta-card recruiter-cta">
            <h3>For Recruiters</h3>
            <p>Find top talent with instant ranking and AI screening.</p>
            <Link to="/login?role=recruiter" className="btn btn-primary">Post a Job</Link>
          </div>
          <div className="cta-card candidate-cta">
            <h3>For Candidates</h3>
            <p>Apply to jobs and get noticed faster.</p>
            <Link to="/login?role=candidate" className="btn btn-accent">Sign Up Now</Link>
          </div>
        </div>
      </section>

      <section className="key-features">
        <div className="container">
          <h2>Key Features</h2>
          <div className="feature-row">
            <div className="feature-chip card">
              <span className="chip-icon">SR</span>
              <div>
                <h3>Smart Resume Parsing</h3>
                <p>Extract skills and experience instantly.</p>
              </div>
            </div>
            <div className="feature-chip card">
              <span className="chip-icon">AR</span>
              <div>
                <h3>AI-Based Ranking</h3>
                <p>Score candidates by job fit automatically.</p>
              </div>
            </div>
            <div className="feature-chip card">
              <span className="chip-icon">FS</span>
              <div>
                <h3>Fast Screening</h3>
                <p>Review top matches in minutes.</p>
              </div>
            </div>
            <div className="feature-chip card">
              <span className="chip-icon">DI</span>
              <div>
                <h3>Data Insights</h3>
                <p>Track applicants and pipeline health.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="how">
        <div className="container how-grid">
          <div className="how-steps">
            <h2>How It Works</h2>
            <div className="how-list">
              <div className="how-item">
                <span className="step-circle">1</span>
                <div>
                  <h4>Sign Up and Login</h4>
                  <p>Create an account for recruiters or candidates.</p>
                </div>
              </div>
              <div className="how-item">
                <span className="step-circle">2</span>
                <div>
                  <h4>Apply for Jobs</h4>
                  <p>Post jobs and receive applications with resumes.</p>
                </div>
              </div>
              <div className="how-item">
                <span className="step-circle">3</span>
                <div>
                  <h4>Get Ranked Results</h4>
                  <p>AI screens resumes and ranks the best candidates.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="how-visual">
            <div className="browser-mock">
              <div className="browser-top">
                <span />
                <span />
                <span />
              </div>
              <div className="browser-body">
                <div className="browser-list">
                  <div className="browser-row">
                    <div className="row-avatar" />
                    <div className="row-lines">
                      <span />
                      <span />
                    </div>
                  </div>
                  <div className="browser-row">
                    <div className="row-avatar" />
                    <div className="row-lines">
                      <span />
                      <span />
                    </div>
                  </div>
                  <div className="browser-row">
                    <div className="row-avatar" />
                    <div className="row-lines">
                      <span />
                      <span />
                    </div>
                  </div>
                </div>
                <div className="browser-checks">
                  <div className="check" />
                  <div className="check" />
                  <div className="check" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-grid">
          <div>
            <h4>About Us</h4>
            <a href="/about">Our Mission</a>
            <a href="/blog">Blog</a>
          </div>
          <div>
            <h4>Quick Links</h4>
            <a href="/jobs">Browse Jobs</a>
            <a href="/login?role=recruiter">Post a Job</a>
          </div>
          <div>
            <h4>Support</h4>
            <a href="/help">Help Center</a>
            <a href="/faq">FAQs</a>
          </div>
          <div>
            <h4>Contact Us</h4>
            <span>contact@resumescreening.com</span>
            <span>+91 123 456 7890</span>
          </div>
        </div>
        <div className="footer-bottom">
          <p>Copyright 2024 Resume Screening. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
