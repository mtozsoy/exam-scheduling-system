import type { ReactNode } from 'react';
import type { PageView } from '../App';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: ReactNode;
  activePage: PageView;
  onNavigate: (page: PageView) => void;
  userRole: string;
  onLogout: () => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, activePage, onNavigate, userRole, onLogout }) => {
  const username = localStorage.getItem('username') || 'Kullanıcı';
  const roleDisplay = userRole === 'admin' ? 'Admin Paneli' : 'Sekreter Paneli';
  
  return (
    <div className="dashboard-wrapper">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-placeholder">FÜ</div>
          <div className="brand-titles">
            <h1>Fırat Üniversitesi</h1>
            <h2>Bilgisayar Mühendisliği</h2>
          </div>
        </div>

        <nav className="sidebar-nav">
          <ul>
            <li><a href="#" className="nav-item">Ana Sayfa</a></li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'scheduling' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('scheduling'); }}
              >
                Sınav Planlama
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'exams' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('exams'); }}
              >
                Sınavlar
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'rooms' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('rooms'); }}
              >
                Derslikler
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'invigilators' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('invigilators'); }}
              >
                Gözetmenler
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'courses' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('courses'); }}
              >
                Dersler
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={`nav-item ${activePage === 'academic_calendars' ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); onNavigate('academic_calendars'); }}
              >
                Akademik Takvim
              </a>
            </li>
            
            {userRole === 'admin' && (
              <li>
                <a 
                  href="#" 
                  className={`nav-item ${activePage === 'users' ? 'active' : ''}`}
                  onClick={(e) => { e.preventDefault(); onNavigate('users'); }}
                >
                  Kullanıcı Yönetimi
                </a>
              </li>
            )}
            
            <li>
              <a 
                href="#" 
                className="nav-item logout-link"
                style={{ color: '#ef4444', marginTop: '1rem' }}
                onClick={(e) => { e.preventDefault(); onLogout(); }}
              >
                Çıkış Yap
              </a>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <p>© 2026 Fırat Üniversitesi</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Top Navbar */}
        <header className="topbar">
          <div className="page-title">
            <h3>
              {activePage === 'scheduling' ? 'Sınav Planlama' : 
               activePage === 'exams' ? 'Sınavlar' : 
               activePage === 'rooms' ? 'Derslikler' : 
               activePage === 'invigilators' ? 'Gözetmenler' : 
               activePage === 'courses' ? 'Dersler' : 
               activePage === 'academic_calendars' ? 'Akademik Takvim' : 
               activePage === 'users' ? 'Kullanıcı Yönetimi' : 'Sayfa'}
            </h3>
          </div>
          <div className="user-profile">
            <div className="avatar">{username.charAt(0).toUpperCase()}</div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
              <span style={{ fontWeight: 600 }}>{username}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{roleDisplay}</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-wrapper">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
