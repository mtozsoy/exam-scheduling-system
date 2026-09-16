import React, { useState, useEffect } from 'react';
import WizardForm from '../components/WizardForm';
import ProposalCard from '../components/ProposalCard';
import { confirmScheduling, getActiveAcademicCalendars } from '../services/api';
import type { Proposal, SchedulingConfirmRequest } from '../types/scheduling';
import type { AcademicCalendar } from '../types/academic_calendars';
import './SchedulingPage.css';

const SchedulingPage: React.FC = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedExamType, setSelectedExamType] = useState<string>('');

  const [confirmingIndex, setConfirmingIndex] = useState<number | null>(null);
  const [confirmedIndex, setConfirmedIndex] = useState<number | null>(null);
  const [confirmError, setConfirmError] = useState<{ [key: number]: string }>({});

  const [activeCalendars, setActiveCalendars] = useState<AcademicCalendar[]>([]);

  useEffect(() => {
    fetchActiveCalendars();
  }, []);

  const fetchActiveCalendars = async () => {
    try {
      const data = await getActiveAcademicCalendars();
      setActiveCalendars(data);
    } catch (err) {
      console.error('Aktif takvimler yüklenemedi:', err);
    }
  };

  const currentActiveCalendar = activeCalendars.find(c => c.exam_type === selectedExamType);

  const handleProposalsReceived = (
    newProposals: Proposal[],
    courseCode: string,
    examType: string
  ) => {
    setProposals(newProposals);
    setSelectedCourse(courseCode);
    setSelectedExamType(examType);
    
    // Yeni proposal'lar geldiğinde state'leri sıfırla
    setConfirmingIndex(null);
    setConfirmedIndex(null);
    setConfirmError({});
  };

  const handleConfirm = async (proposal: Proposal, index: number) => {
    setConfirmingIndex(index);
    setConfirmError(prev => ({ ...prev, [index]: '' }));

    try {
      const request: SchedulingConfirmRequest = {
        course_code: selectedCourse,
        exam_type: selectedExamType,
        date: proposal.date,
        start_time: proposal.start_time,
        end_time: proposal.end_time,
        total_students: proposal.total_students,
        rooms: proposal.rooms.map(r => ({
          room_code: r.room_code,
          invigilator_id: r.invigilator_id
        }))
      };

      const response = await confirmScheduling(request);

      if (response.success) {
        setConfirmedIndex(index);
      } else {
        setConfirmError(prev => ({ ...prev, [index]: response.message || 'Bilinmeyen bir hata oluştu.' }));
      }
    } catch (err: any) {
      setConfirmError(prev => ({ ...prev, [index]: err.message || 'Onay işlemi sırasında hata oluştu.' }));
    } finally {
      setConfirmingIndex(null);
    }
  };

  return (
    <div className="scheduling-page">
      <div className="page-header-desc">
        <p>Dersiniz için akademik takvime ve mevcut kaynaklara uygun sınav planı oluşturun.</p>
      </div>

      <div className="page-content-grid">
        {/* Sol Kolon */}
        <div className="left-column">
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
                  <ProposalCard
                    key={index}
                    proposal={proposal}
                    isConfirming={confirmingIndex === index}
                    isConfirmed={confirmedIndex === index}
                    confirmError={confirmError[index] || null}
                    onConfirm={() => handleConfirm(proposal, index)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sağ Kolon */}
        <div className="right-column">
          <div className="info-panel">
            <h3>Planlama Bilgileri</h3>
            <div className="info-section">
              <div className="info-item">
                <span className="info-label">Aktif Dönem:</span>
                <span className="info-value">
                  {currentActiveCalendar ? `${currentActiveCalendar.academic_year} ${currentActiveCalendar.semester}` : '-'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Sınav Türü:</span>
                <span className="info-value">
                  {selectedExamType || '-'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Takvim Aralığı:</span>
                <span className="info-value">
                  {currentActiveCalendar 
                    ? `${new Date(currentActiveCalendar.start_date).toLocaleDateString('tr-TR')} - ${new Date(currentActiveCalendar.end_date).toLocaleDateString('tr-TR')}` 
                    : '-'}
                </span>
              </div>
            </div>

            <div className="checks-section">
              <h4>Sistem Kontrolleri</h4>
              <ul className="check-list">
                <li><span className="check-icon">✓</span> Öğrenci sınav çakışması</li>
                <li><span className="check-icon">✓</span> Derslik uygunluğu</li>
                <li><span className="check-icon">✓</span> Gözetmen uygunluğu</li>
                <li><span className="check-icon">✓</span> Derslik kapasitesi</li>
                <li><span className="check-icon">✓</span> Akademik takvim uygunluğu</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulingPage;
