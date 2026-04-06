import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './RoleSelection.css';

export default function RoleSelection() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  const handleRoleSelect = (role) => {
    navigate(`/login?role=${role}`);
  };

  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="role-selection-page">
      <Navbar user={user} role={localStorage.getItem('role')} />
      <div className="role-selection-container">
        <div className="role-selection-card card">
          <button className="back-button" onClick={handleBack}>
            ← Back
          </button>
          <h1>Welcome to ResumeScreen AI</h1>
          <p className="role-selection-subtitle">Please select your role to continue</p>

          <div className="role-select">
            <h3>I am a...</h3>
            <div className="role-buttons">
              <button
                className="btn btn-primary role-btn"
                onClick={() => handleRoleSelect('candidate')}
              >
                <div className="role-icon">👤</div>
                <div className="role-content">
                  <h4>Candidate</h4>
                  <p>Apply for jobs and get noticed faster</p>
                </div>
              </button>
              <button
                className="btn btn-outline role-btn"
                onClick={() => handleRoleSelect('recruiter')}
              >
                <div className="role-icon">🏢</div>
                <div className="role-content">
                  <h4>Recruiter</h4>
                  <p>Find top talent with AI-powered screening</p>
                </div>
              </button>
              <button
                className="btn btn-ghost role-btn"
                onClick={() => handleRoleSelect('admin')}
              >
                <div className="role-icon">⚙️</div>
                <div className="role-content">
                  <h4>Admin</h4>
                  <p>Manage the system and oversee operations</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
