import { useState, useEffect } from 'react';
import DashboardLayout from './layouts/DashboardLayout';
import SchedulingPage from './pages/SchedulingPage';
import ExamsPage from './pages/ExamsPage';
import RoomsPage from './pages/RoomsPage';
import InvigilatorsPage from './pages/InvigilatorsPage';
import CoursesPage from './pages/CoursesPage';
import AcademicCalendarsPage from './pages/AcademicCalendarsPage';
import UsersPage from './pages/UsersPage';
import LoginPage from './pages/LoginPage';
import './App.css';

export type PageView = 'scheduling' | 'exams' | 'rooms' | 'invigilators' | 'courses' | 'academic_calendars' | 'users';

function App() {
  const [activePage, setActivePage] = useState<PageView>('scheduling');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userRole, setUserRole] = useState<string>('');
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    if (token) {
      setIsAuthenticated(true);
      setUserRole(role || '');
    }
  }, []);
  
  const handleLoginSuccess = (token: string, role: string, username: string) => {
    localStorage.setItem('token', token);
    localStorage.setItem('role', role);
    localStorage.setItem('username', username);
    setIsAuthenticated(true);
    setUserRole(role);
  };
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setUserRole('');
  };
  
  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="App">
      <DashboardLayout activePage={activePage} onNavigate={setActivePage} userRole={userRole} onLogout={handleLogout}>
        {activePage === 'scheduling' && <SchedulingPage />}
        {activePage === 'exams' && <ExamsPage />}
        {activePage === 'rooms' && <RoomsPage />}
        {activePage === 'invigilators' && <InvigilatorsPage />}
        {activePage === 'courses' && <CoursesPage />}
        {activePage === 'academic_calendars' && <AcademicCalendarsPage />}
        {activePage === 'users' && userRole === 'admin' && <UsersPage />}
      </DashboardLayout>
    </div>
  );
}

export default App; // forced update
