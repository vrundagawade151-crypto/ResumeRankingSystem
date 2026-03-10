import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { sendOTP, verifyOTP, loginDirect } from '../api';
import Navbar from '../components/Navbar';
import './Login.css';

export default function Login() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const roleParam = searchParams.get('role') || 'candidate';

  const getInitialStep = () => {
    if (roleParam === 'admin') return 'direct';
    if (roleParam === 'candidate' || roleParam === 'recruiter') return 'email';
    return 'role';
  };
  const [step, setStep] = useState(getInitialStep()); // role | email | otp | direct
  const [role, setRole] = useState(roleParam || 'candidate');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [demoOtp, setDemoOtp] = useState('');

  useEffect(() => {
    setRole(roleParam);
  }, [roleParam]);

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await sendOTP(email, role, { name, company_name: companyName, phone });
      setDemoOtp(res.data.otp);
      setStep('otp');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await verifyOTP(email, otp, role);
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      localStorage.setItem('profile', JSON.stringify(res.data.profile));
      localStorage.setItem('role', res.data.role);
      if (res.data.role === 'candidate') navigate('/candidate');
      else if (res.data.role === 'recruiter') navigate('/recruiter');
      else navigate('/admin');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await loginDirect(email, password, 'admin');
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      localStorage.setItem('profile', JSON.stringify(res.data.profile));
      localStorage.setItem('role', 'admin');
      navigate('/admin');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const user = JSON.parse(localStorage.getItem('user') || 'null');

  return (
    <div className="login-page">
      <Navbar user={user} role={localStorage.getItem('role')} />
      <div className="login-container">
        <div className="login-card card">
          <h1>Welcome</h1>
          <p className="login-subtitle">AI Resume Screening & Ranking System</p>

          {/* Role selection */}
          {step === 'role' && (
            <div className="role-select">
              <h3>I am a...</h3>
              <div className="role-buttons">
                <button
                  className={`btn ${role === 'candidate' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => { setRole('candidate'); setStep('email'); }}
                >Candidate</button>
                <button
                  className={`btn ${role === 'recruiter' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => { setRole('recruiter'); setStep('email'); }}
                >Recruiter</button>
                <button
                  className={`btn ${role === 'admin' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => { setRole('admin'); setStep('direct'); }}
                >Admin</button>
              </div>
            </div>
          )}

          {/* OTP flow - email */}
          {step === 'email' && (
            <form onSubmit={handleSendOTP}>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
              </div>
              {role === 'recruiter' && (
                <>
                  <div className="form-group">
                    <label>Full Name</label>
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="John Doe" />
                  </div>
                  <div className="form-group">
                    <label>Company Name</label>
                    <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="Acme Inc" />
                  </div>
                </>
              )}
              {role === 'candidate' && (
                <div className="form-group">
                  <label>Full Name</label>
                  <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
                </div>
              )}
              {error && <p className="error">{error}</p>}
              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? 'Sending...' : 'Send OTP'}
              </button>
              <button type="button" className="btn btn-ghost btn-block" onClick={() => setStep('role')}>Back</button>
            </form>
          )}

          {/* OTP verification */}
          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP}>
              <div className="form-group">
                <label>Enter OTP</label>
                <input type="text" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="123456" maxLength={6} required />
              </div>
              {demoOtp && <p className="demo-otp">Demo OTP: <strong>{demoOtp}</strong></p>}
              {error && <p className="error">{error}</p>}
              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? 'Verifying...' : 'Verify & Login'}
              </button>
              <button type="button" className="btn btn-ghost btn-block" onClick={() => setStep('email')}>Back</button>
            </form>
          )}

          {/* Admin direct login */}
          {step === 'direct' && (
            <form onSubmit={handleAdminLogin}>
              <div className="form-group">
                <label>Admin Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@resumescreen.com" required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="admin123" required />
              </div>
              <p className="hint">Default: admin@resumescreen.com / admin123</p>
              {error && <p className="error">{error}</p>}
              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </button>
              <button type="button" className="btn btn-ghost btn-block" onClick={() => setStep('role')}>Back</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
