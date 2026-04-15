import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import RoleSelection from './pages/RoleSelection';
import Login from './pages/Login';
import CandidateDashboard from './pages/CandidateDashboard';
import RecruiterLayout from './components/RecruiterLayout';
import RecruiterDashboard from './pages/RecruiterDashboard';
import JobPosting from './pages/JobPosting';
import ApplicantList from './pages/ApplicantList';
import ResumeRanking from './pages/ResumeRanking';
import JobReport from './pages/JobReport';
import AdminDashboard from './pages/AdminDashboard';

function ProtectedRoute({ children, roles = [] }) {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token) return <Navigate to="/login" replace />;
  if (roles.length && !roles.includes(role)) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/role-selection" element={<RoleSelection />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/candidate"
          element={
            <ProtectedRoute roles={['candidate']}>
              <CandidateDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recruiter"
          element={
            <ProtectedRoute roles={['recruiter']}>
              <RecruiterLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<RecruiterDashboard />} />
          <Route path="jobs/new" element={<JobPosting />} />
          <Route path="jobs/:jobId/applicants" element={<ApplicantList />} />
          <Route path="jobs/:jobId/ranking" element={<ResumeRanking />} />
          <Route path="reports/:jobId" element={<JobReport />} />
        </Route>
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
