import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './Landing.css';

export default function Landing() {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const role = localStorage.getItem('role');

  return (
    <div className="landing">
      <Navbar user={user} role={role} />
      
      {/* Hero */}
      <section className="hero">
        <div className="container hero-content">
          <h1>AI-Powered Resume Screening & Ranking</h1>
          <p>Streamline your hiring with intelligent resume parsing, skill matching, and automated candidate ranking.</p>
          <div className="hero-buttons">
            <Link to="/login" className="btn btn-primary btn-lg">Get Started</Link>
            <Link to="/login" className="btn btn-outline btn-lg">Login</Link>
            <Link to="/login?role=admin" className="btn btn-ghost btn-lg" style={{ color: 'white', border: '1px solid rgba(255,255,255,0.5)' }}>Admin</Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="container">
          <h2>Why Choose ResumeScreen AI</h2>
          <div className="features-grid">
            <div className="feature-card card">
              <span className="feature-icon">🤖</span>
              <h3>AI Resume Parsing</h3>
              <p>Extract skills, education, and experience from PDF and Word documents using advanced NLP.</p>
            </div>
            <div className="feature-card card">
              <span className="feature-icon">📊</span>
              <h3>Smart Ranking</h3>
              <p>60% skill match, 20% experience, 20% education — rank candidates by job fit automatically.</p>
            </div>
            <div className="feature-card card">
              <span className="feature-icon">⚡</span>
              <h3>Save Time</h3>
              <p>Reduce screening time by 80%. Focus on top candidates first.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="how-it-works">
        <div className="container">
          <h2>How It Works</h2>
          <div className="steps">
            <div className="step">
              <span className="step-num">1</span>
              <h4>Post Jobs</h4>
              <p>Recruiters create job postings with required skills and experience.</p>
            </div>
            <div className="step">
              <span className="step-num">2</span>
              <h4>Receive Applications</h4>
              <p>Candidates apply with their resume. All applications are stored securely.</p>
            </div>
            <div className="step">
              <span className="step-num">3</span>
              <h4>AI Screening</h4>
              <p>Click Extract — our AI parses resumes and ranks candidates by job match.</p>
            </div>
            <div className="step">
              <span className="step-num">4</span>
              <h4>Hire Faster</h4>
              <p>Review the ranked list and shortlist the best candidates.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTAs */}
      <section className="cta-section">
        <div className="container cta-grid">
          <div className="cta-card recruiter-cta">
            <h3>I'm a Recruiter</h3>
            <p>Post jobs, receive applications, and screen candidates with AI.</p>
            <Link to="/login?role=recruiter" className="btn btn-primary">Recruiter Login</Link>
          </div>
          <div className="cta-card candidate-cta">
            <h3>I'm a Candidate</h3>
            <p>Browse jobs, apply with your resume, and get noticed by top companies.</p>
            <Link to="/login?role=candidate" className="btn btn-accent">Candidate Login</Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>© 2024 ResumeScreen AI — AI-Based Resume Screening & Ranking System</p>
        </div>
      </footer>
    </div>
  );
}
