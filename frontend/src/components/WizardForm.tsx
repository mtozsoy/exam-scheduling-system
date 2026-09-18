import React, { useState, useEffect } from 'react';
import { getCourses, getSchedulingProposals, getExams } from '../services/api';
import type { Course, Proposal } from '../types/scheduling';
import type { Exam } from '../types/exams';
import './WizardForm.css';

interface WizardFormProps {
  onProposalsReceived: (proposals: Proposal[], courseCode: string, examType: string) => void;
}

const WizardForm: React.FC<WizardFormProps> = ({ onProposalsReceived }) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [scheduledExams, setScheduledExams] = useState<Exam[]>([]);
  const [loadingData, setLoadingData] = useState<boolean>(true);
  const [initError, setInitError] = useState<string | null>(null);

  const [courseCode, setCourseCode] = useState<string>('');
  const [examType, setExamType] = useState<string>('Vize');
  const [durationMinutes, setDurationMinutes] = useState<number>(90);
  const [dailyStartTime, setDailyStartTime] = useState<string>('09:00');
  const [dailyEndTime, setDailyEndTime] = useState<string>('17:00');

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoadingData(true);
        const [coursesData, examsData] = await Promise.all([
          getCourses(),
          getExams()
        ]);
        
        setCourses(coursesData);
        setScheduledExams(examsData);
        
        if (coursesData.length > 0) {
          setCourseCode(coursesData[0].course_code);
        }
      } catch (err: any) {
        setInitError(err.message || 'Veriler yüklenirken bir hata oluştu.');
      } finally {
        setLoadingData(false);
      }
    };
    fetchData();
  }, []);

  // Update selected course if the current one is now disabled due to examType change
  useEffect(() => {
    if (courses.length > 0) {
      const isCurrentScheduled = scheduledExams.some(
        e => e.course_code === courseCode && e.exam_type === examType
      );
      
      if (isCurrentScheduled) {
        // Find first available course
        const firstAvailable = courses.find(
          c => !scheduledExams.some(e => e.course_code === c.course_code && e.exam_type === examType)
        );
        if (firstAvailable) {
          setCourseCode(firstAvailable.course_code);
        } else {
          setCourseCode(''); // No courses available
        }
      }
    }
  }, [examType, scheduledExams, courses, courseCode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    if (!courseCode) {
      setSubmitError('Planlanacak uygun ders bulunamadı. Lütfen önce ders ekleyin veya sistemdeki tüm derslerin planlanıp planlanmadığını kontrol edin.');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await getSchedulingProposals({
        course_code: courseCode,
        exam_type: examType,
        duration_minutes: durationMinutes,
        daily_start_time: `${dailyStartTime}:00`, // Backend expects HH:MM:SS
        daily_end_time: `${dailyEndTime}:00`
      });

      if (response.success && response.proposals) {
        onProposalsReceived(response.proposals, courseCode, examType);
      } else {
        setSubmitError(response.message || 'Bilinmeyen bir hata oluştu.');
      }
    } catch (err: any) {
      setSubmitError(err.message || 'Planlama önerileri alınırken hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loadingData) {
    return <div className="wizard-card loading">Veriler Yükleniyor...</div>;
  }

  if (initError) {
    return <div className="wizard-card error">Hata: {initError}</div>;
  }

  return (
    <div className="wizard-card">
      <div className="wizard-header">
        <h2>Sınav Planlama Sihirbazı</h2>
        <p>Akademik takvime uygun sınav tarih ve derslik önerilerini alın.</p>
      </div>

      <form className="wizard-form" onSubmit={handleSubmit}>
        {submitError && <div className="alert-error">{submitError}</div>}
        
        <div className="form-group">
          <label htmlFor="courseCode">Ders</label>
          <select 
            id="courseCode"
            value={courseCode} 
            onChange={(e) => setCourseCode(e.target.value)}
            required
          >
            {courses.map(c => {
              const isScheduled = scheduledExams.some(e => e.course_code === c.course_code && e.exam_type === examType);
              return (
                <option key={c.course_code} value={c.course_code} disabled={isScheduled}>
                  {c.course_code} - {c.course_name} {isScheduled ? "(Planlandı)" : ""}
                </option>
              );
            })}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="examType">Sınav Türü</label>
            <select 
              id="examType"
              value={examType} 
              onChange={(e) => setExamType(e.target.value)}
              required
            >
              <option value="Vize">Vize</option>
              <option value="Final">Final</option>
              <option value="Bütünleme">Bütünleme</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="durationMinutes">Süre (Dakika)</label>
            <input 
              type="number" 
              id="durationMinutes"
              min="15" 
              max="240" 
              value={durationMinutes} 
              onChange={(e) => setDurationMinutes(Number(e.target.value))}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="dailyStartTime">Günlük Başlangıç</label>
            <input 
              type="time" 
              id="dailyStartTime"
              value={dailyStartTime} 
              onChange={(e) => setDailyStartTime(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="dailyEndTime">Günlük Bitiş</label>
            <input 
              type="time" 
              id="dailyEndTime"
              value={dailyEndTime} 
              onChange={(e) => setDailyEndTime(e.target.value)}
              required
            />
          </div>
        </div>

        <button 
          type="submit" 
          className="btn-primary submit-btn" 
          disabled={isSubmitting || !courseCode}
        >
          {isSubmitting ? 'Hesaplanıyor...' : 'Plan Öner'}
        </button>
      </form>
    </div>
  );
};

export default WizardForm;
