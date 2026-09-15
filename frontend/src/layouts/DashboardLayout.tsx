import type { ReactNode } from 'react';
import type { PageView } from '../App';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: ReactNode;
  activePage: PageView;
  onNavigate: (page: PageView) => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, activePage, onNavigate }) => {
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
            <li><a href="#" className="nav-item">Dersler</a></li>
            <li><a href="#" className="nav-item">Akademik Takvim</a></li>
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
               activePage === 'invigilators' ? 'Gözetmenler' : 'Sayfa'}
            </h3>
          </div>
          <div className="user-profile">
            <div className="avatar">A</div>
            <span>Admin Paneli</span>
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
