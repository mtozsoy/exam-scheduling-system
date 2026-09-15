import { useState } from 'react';
import DashboardLayout from './layouts/DashboardLayout';
import SchedulingPage from './pages/SchedulingPage';
import ExamsPage from './pages/ExamsPage';
import RoomsPage from './pages/RoomsPage';
import InvigilatorsPage from './pages/InvigilatorsPage';
import CoursesPage from './pages/CoursesPage';
import './App.css';

export type PageView = 'scheduling' | 'exams' | 'rooms' | 'invigilators' | 'courses';

function App() {
  const [activePage, setActivePage] = useState<PageView>('scheduling');

  return (
    <div className="App">
      <DashboardLayout activePage={activePage} onNavigate={setActivePage}>
        {activePage === 'scheduling' && <SchedulingPage />}
        {activePage === 'exams' && <ExamsPage />}
        {activePage === 'rooms' && <RoomsPage />}
        {activePage === 'invigilators' && <InvigilatorsPage />}
        {activePage === 'courses' && <CoursesPage />}
      </DashboardLayout>
    </div>
  );
}

export default App; // forced update
