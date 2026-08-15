
import DashboardLayout from './layouts/DashboardLayout';
import SchedulingPage from './pages/SchedulingPage';
import './App.css';

function App() {
  return (
    <div className="App">
      <DashboardLayout>
        <SchedulingPage />
      </DashboardLayout>
    </div>
  );
}

export default App;
