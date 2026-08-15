import type { ReactNode } from 'react';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
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
            <li><a href="#" className="nav-item active">Sınav Planlama</a></li>
            <li><a href="#" className="nav-item">Sınavlar</a></li>
            <li><a href="#" className="nav-item">Derslikler</a></li>
            <li><a href="#" className="nav-item">Gözetmenler</a></li>
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
            <h3>Sınav Planlama</h3>
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
