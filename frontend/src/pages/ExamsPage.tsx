import React, { useState, useEffect } from 'react';
import { getExams, getCourses, updateExam, deleteExam } from '../services/api';
import type { Exam, ExamUpdateData } from '../types/exams';
import type { Course } from '../types/scheduling';
import './ExamsPage.css';

const ExamsPage: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  
  // Filters
  const [courseFilter, setCourseFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  // Modal State
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editData, setEditData] = useState<ExamUpdateData>({
    exam_type: '',
    date: '',
    start_time: '',
    duration_minutes: 0,
  });
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  useEffect(() => {
    fetchExams();
    fetchCourses();
  }, []);

  const fetchExams = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getExams();
      setExams(data);
    } catch (err: any) {
      setError(err.message || 'Sınavlar yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const data = await getCourses();
      setCourses(data);
    } catch (err: any) {
      console.error("Dersler yüklenemedi", err);
    }
  };

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('tr-TR', options);
  };

  const formatTime = (timeString: string) => {
    if (!timeString) return '';
    const parts = timeString.split(':');
    return `${parts[0]}:${parts[1]}`;
  };

  const filteredExams = exams.filter(exam => {
    if (courseFilter && exam.course_code !== courseFilter) return false;
    if (typeFilter && exam.exam_type !== typeFilter) return false;
    return true;
  });

  const handleDelete = async (examId: number, courseCode: string) => {
    const isConfirmed = window.confirm(`${courseCode} dersine ait bu sınavı silmek istediğinize emin misiniz?`);
    if (!isConfirmed) return;
    
    try {
      await deleteExam(examId);
      setSuccessMsg('Sınav başarıyla silindi.');
      fetchExams();
    } catch (err: any) {
      setError(`Silme işlemi başarısız: ${err.message}`);
    }
  };

  const openEditModal = (exam: Exam) => {
    setSelectedExam(exam);
    setIsEditing(true);
    setEditData({
      exam_type: exam.exam_type,
      date: exam.date,
      start_time: exam.start_time,
      duration_minutes: exam.duration_minutes
    });
    setSuccessMsg(null);
    setError(null);
  };

  const openDetailModal = (exam: Exam) => {
    setSelectedExam(exam);
    setIsEditing(false);
    setSuccessMsg(null);
    setError(null);
  };

  const handleUpdate = async () => {
    if (!selectedExam) return;
    try {
      setIsUpdating(true);
      setError(null);
      await updateExam(selectedExam.exam_id, editData);
      setSuccessMsg("Sınav başarıyla güncellendi.");
      setIsEditing(false);
      setSelectedExam(null);
      fetchExams();
    } catch (err: any) {
      setError(err.message || "Güncelleme sırasında bir hata oluştu.");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="exams-page">
      <div className="page-header-desc">
        <p>Sistemde planlanmış sınavları görüntüleyin.</p>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {error && !selectedExam && <div className="alert-error">✕ {error}</div>}

      <div className="exams-filters">
        <div className="filter-group">
          <label>Ders</label>
          <select value={courseFilter} onChange={e => setCourseFilter(e.target.value)}>
            <option value="">Tüm Dersler</option>
            {courses.map(c => (
              <option key={c.course_code} value={c.course_code}>{c.course_code}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Sınav Türü</label>
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
            <option value="">Tümü</option>
            <option value="Vize">Vize</option>
            <option value="Final">Final</option>
            <option value="Bütünleme">Bütünleme</option>
          </select>
        </div>
      </div>

      <div className="exams-content">
        {loading && <div className="loading-state">Sınavlar yükleniyor...</div>}
        
        {!loading && filteredExams.length === 0 && (
          <div className="empty-state">Kriterlere uygun sınav bulunmuyor.</div>
        )}

        {!loading && filteredExams.length > 0 && (
          <div className="table-container">
            <table className="exams-table">
              <thead>
                <tr>
                  <th>Ders</th>
                  <th>Sınav Türü</th>
                  <th>Tarih</th>
                  <th>Başlangıç</th>
                  <th>Süre</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {filteredExams.map(exam => (
                  <tr key={exam.exam_id}>
                    <td className="fw-600">{exam.course_code}</td>
                    <td>{exam.exam_type}</td>
                    <td>{formatDate(exam.date)}</td>
                    <td>{formatTime(exam.start_time)}</td>
                    <td>{exam.duration_minutes} dk</td>
                    <td className="actions-cell">
                      <button 
                        className="btn-details"
                        onClick={() => openDetailModal(exam)}
                      >
                        Detay
                      </button>
                      <button 
                        className="btn-edit"
                        onClick={() => openEditModal(exam)}
                      >
                        Düzenle
                      </button>
                      <button 
                        className="btn-delete"
                        onClick={() => handleDelete(exam.exam_id, exam.course_code)}
                      >
                        Sil
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedExam && (
        <div className="modal-overlay" onClick={() => !isUpdating && setSelectedExam(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{isEditing ? 'Sınavı Düzenle' : 'Sınav Detayı'}</h3>
              {!isUpdating && (
                <button className="btn-close" onClick={() => setSelectedExam(null)}>×</button>
              )}
            </div>
            <div className="modal-body">
              {error && isEditing && <div className="alert-error">{error}</div>}

              {isEditing ? (
                <>
                  <div className="detail-row">
                    <span className="detail-label">Ders Kodu:</span>
                    <span className="detail-value">{selectedExam.course_code}</span>
                  </div>
                  <div className="form-group">
                    <label>Sınav Türü</label>
                    <select 
                      value={editData.exam_type} 
                      onChange={e => setEditData({...editData, exam_type: e.target.value})}
                      disabled={isUpdating}
                    >
                      <option value="Vize">Vize</option>
                      <option value="Final">Final</option>
                      <option value="Bütünleme">Bütünleme</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Tarih</label>
                    <input 
                      type="date" 
                      value={editData.date}
                      onChange={e => setEditData({...editData, date: e.target.value})}
                      disabled={isUpdating}
                    />
                  </div>
                  <div className="form-group">
                    <label>Başlangıç Saati</label>
                    <input 
                      type="time" 
                      value={formatTime(editData.start_time)}
                      onChange={e => setEditData({...editData, start_time: e.target.value + ":00"})}
                      disabled={isUpdating}
                    />
                  </div>
                  <div className="form-group">
                    <label>Süre (dk)</label>
                    <input 
                      type="number" 
                      min="15"
                      step="15"
                      value={editData.duration_minutes}
                      onChange={e => setEditData({...editData, duration_minutes: parseInt(e.target.value) || 0})}
                      disabled={isUpdating}
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="detail-row">
                    <span className="detail-label">Sınav ID:</span>
                    <span className="detail-value">{selectedExam.exam_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Ders Kodu:</span>
                    <span className="detail-value">{selectedExam.course_code}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Sınav Türü:</span>
                    <span className="detail-value">{selectedExam.exam_type}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Tarih:</span>
                    <span className="detail-value">{formatDate(selectedExam.date)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Saat:</span>
                    <span className="detail-value">{formatTime(selectedExam.start_time)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Süre:</span>
                    <span className="detail-value">{selectedExam.duration_minutes} dk</span>
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              {isEditing ? (
                <>
                  <button 
                    className="btn-secondary" 
                    onClick={() => setSelectedExam(null)}
                    disabled={isUpdating}
                  >
                    İptal
                  </button>
                  <button 
                    className="btn-primary" 
                    onClick={handleUpdate}
                    disabled={isUpdating}
                  >
                    {isUpdating ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
                  </button>
                </>
              ) : (
                <button className="btn-primary" onClick={() => setSelectedExam(null)}>Kapat</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExamsPage;
