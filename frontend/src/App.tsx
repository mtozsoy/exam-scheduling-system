import { useState } from 'react';
import DashboardLayout from './layouts/DashboardLayout';
import SchedulingPage from './pages/SchedulingPage';
import ExamsPage from './pages/ExamsPage';
import './App.css';

export type PageView = 'scheduling' | 'exams';

function App() {
  const [activePage, setActivePage] = useState<PageView>('scheduling');

  return (
    <div className="App">
      <DashboardLayout activePage={activePage} onNavigate={setActivePage}>
        {activePage === 'scheduling' && <SchedulingPage />}
        {activePage === 'exams' && <ExamsPage />}
      </DashboardLayout>
    </div>
  );
}

export default App; // forced update
