import { useState } from 'react';
import DashboardLayout from './layouts/DashboardLayout';
import SchedulingPage from './pages/SchedulingPage';
import ExamsPage from './pages/ExamsPage';
import RoomsPage from './pages/RoomsPage';
import './App.css';

export type PageView = 'scheduling' | 'exams' | 'rooms';

function App() {
  const [activePage, setActivePage] = useState<PageView>('scheduling');

  return (
    <div className="App">
      <DashboardLayout activePage={activePage} onNavigate={setActivePage}>
        {activePage === 'scheduling' && <SchedulingPage />}
        {activePage === 'exams' && <ExamsPage />}
        {activePage === 'rooms' && <RoomsPage />}
      </DashboardLayout>
    </div>
  );
}

export default App; // forced update
