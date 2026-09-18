import React, { useState, useEffect } from 'react';
import { getCourses, createCourse, updateCourse, deleteCourse } from '../services/api';
import type { Course, CourseCreateData, CourseUpdateData } from '../types/courses';
import './CoursesPage.css';

const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [selectedCourseCode, setSelectedCourseCode] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<CourseCreateData>({
    course_code: '',
    course_name: '',
    term: 1,
    semester: 1
  });
  
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCourses();
      setCourses(data);
    } catch (err: any) {
      setError(err.message || 'Dersler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setIsEditing(false);
    setSelectedCourseCode(null);
    setFormData({ course_code: '', course_name: '', term: 1, semester: 1 });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const openEditModal = (course: Course) => {
    setIsEditing(true);
    setSelectedCourseCode(course.course_code);
    setFormData({
      course_code: course.course_code,
      course_name: course.course_name,
      term: course.term,
      semester: course.semester
    });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    if (isSubmitting) return;
    setIsModalOpen(false);
    setError(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setError(null);

      if (isEditing && selectedCourseCode) {
        const updateData: CourseUpdateData = {
          course_name: formData.course_name,
          term: formData.term,
          semester: formData.semester
        };
        await updateCourse(selectedCourseCode, updateData);
        setSuccessMsg('Ders başarıyla güncellendi.');
      } else {
        await createCourse(formData);
        setSuccessMsg('Ders başarıyla eklendi.');
      }
      
      closeModal();
      fetchCourses();
    } catch (err: any) {
      setError(err.message || 'İşlem sırasında bir hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (course: Course) => {
    const isConfirmed = window.confirm(`"${course.course_code} - ${course.course_name}" kodlu dersi silmek istediğinize emin misiniz?`);
    if (!isConfirmed) return;
    
    try {
      setError(null);
      setSuccessMsg(null);
      await deleteCourse(course.course_code);
      setSuccessMsg('Ders başarıyla silindi.');
      fetchCourses();
    } catch (err: any) {
      setError(`Silme işlemi başarısız: ${err.message}`);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header-desc">
        <p>Sistemdeki dersleri görüntüleyin, yeni ders ekleyin veya mevcut olanları düzenleyin.</p>
        <button className="btn-primary" onClick={openAddModal}>+ Yeni Ders Ekle</button>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {error && !isModalOpen && <div className="alert-error">✕ {error}</div>}

      <div className="page-content">
        {loading && <div className="loading-state">Dersler yükleniyor...</div>}
        
        {!loading && courses.length === 0 && (
          <div className="empty-state">Sistemde henüz ders bulunmuyor.</div>
        )}

        {!loading && courses.length > 0 && (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ders Kodu</th>
                  <th>Ders Adı</th>
                  <th>Dönem</th>
                  <th>Yarıyıl</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {courses.map(course => (
                  <tr key={course.course_code}>
                    <td className="fw-600">{course.course_code}</td>
                    <td>{course.course_name}</td>
                    <td>{course.term}</td>
                    <td>{course.semester}</td>
                    <td className="actions-cell">
                      <button 
                        className="btn-edit"
                        onClick={() => openEditModal(course)}
                      >
                        Düzenle
                      </button>
                      <button 
                        className="btn-delete"
                        onClick={() => handleDelete(course)}
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
      {isModalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{isEditing ? 'Ders Düzenle' : 'Yeni Ders Ekle'}</h3>
              {!isSubmitting && (
                <button className="btn-close" onClick={closeModal}>×</button>
              )}
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && isModalOpen && <div className="alert-error">{error}</div>}

                <div className="form-group">
                  <label>Ders Kodu</label>
                  <input 
                    type="text" 
                    value={formData.course_code}
                    onChange={e => setFormData({...formData, course_code: e.target.value})}
                    disabled={isEditing || isSubmitting}
                    required
                    placeholder="Örn: AIT209"
                  />
                  {isEditing && <small className="text-muted">Ders kodu sonradan değiştirilemez.</small>}
                </div>

                <div className="form-group">
                  <label>Ders Adı</label>
                  <input 
                    type="text" 
                    value={formData.course_name}
                    onChange={e => setFormData({...formData, course_name: e.target.value})}
                    disabled={isSubmitting}
                    required
                    placeholder="Örn: Atatürk İlkeleri ve İnkılap Tarihi"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Dönem</label>
                    <input 
                      type="number" 
                      value={formData.term}
                      onChange={e => setFormData({...formData, term: parseInt(e.target.value, 10) || 1})}
                      disabled={isSubmitting}
                      required
                      min="1"
                    />
                  </div>
                  <div className="form-group">
                    <label>Yarıyıl</label>
                    <input 
                      type="number" 
                      value={formData.semester}
                      onChange={e => setFormData({...formData, semester: parseInt(e.target.value, 10) || 1})}
                      disabled={isSubmitting}
                      required
                      min="1"
                    />
                  </div>
                </div>

              </div>
              <div className="modal-footer">
                <button 
                  type="button"
                  className="btn-secondary" 
                  onClick={closeModal}
                  disabled={isSubmitting}
                >
                  İptal
                </button>
                <button 
                  type="submit"
                  className="btn-primary" 
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Kaydediliyor...' : 'Kaydet'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoursesPage;
