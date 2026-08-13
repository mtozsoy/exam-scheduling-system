import React, { useState } from 'react';
import WizardForm from '../components/WizardForm';
import type { Proposal } from '../types/scheduling';
import './SchedulingPage.css';

const SchedulingPage: React.FC = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedExamType, setSelectedExamType] = useState<string>('');

  const handleProposalsReceived = (
    newProposals: Proposal[],
    courseCode: string,
    examType: string
  ) => {
    setProposals(newProposals);
    setSelectedCourse(courseCode);
    setSelectedExamType(examType);
  };

  return (
    <div className="scheduling-page">
      <div className="wizard-container">
        <WizardForm onProposalsReceived={handleProposalsReceived} />
      </div>

      {proposals.length > 0 && (
        <div className="proposals-container">
          <h3>
            {selectedCourse} - {selectedExamType} Sınavı İçin Öneriler
          </h3>
          <div className="proposals-list">
            {proposals.map((proposal, index) => (
              <div key={index} className="simple-proposal-item">
                <div className="proposal-header">
                  <strong>Tarih:</strong> {proposal.date} <br />
                  <strong>Saat:</strong> {proposal.start_time} - {proposal.end_time}
                </div>
                <div className="proposal-rooms">
                  <strong>Atanan Derslikler:</strong>
                  <ul>
                    {proposal.rooms.map((room, rIdx) => (
                      <li key={rIdx}>
                        {room.room_code} (Kapasite: {room.capacity}, Atanan: {room.assigned_count})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SchedulingPage;
