import React, { useState, useEffect } from 'react';
import { getAcademicCalendars, createAcademicCalendar, updateAcademicCalendar, deleteAcademicCalendar } from '../services/api';
import type { AcademicCalendar, AcademicCalendarCreateData, AcademicCalendarUpdateData } from '../types/academic_calendars';
import './AcademicCalendarsPage.css';

const AcademicCalendarsPage: React.FC = () => {
  const [calendars, setCalendars] = useState<AcademicCalendar[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [selectedCalendarId, setSelectedCalendarId] = useState<number | null>(null);
  
  const [formData, setFormData] = useState<AcademicCalendarCreateData>({
    academic_year: '2026-2027',
    semester: 'Güz',
    exam_type: 'Vize',
    start_date: '',
    end_date: '',
    is_active: false
  });
  
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    fetchCalendars();
  }, []);

  const fetchCalendars = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAcademicCalendars();
      setCalendars(data);
    } catch (err: any) {
      setError(err.message || 'Takvimler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setIsEditing(false);
    setSelectedCalendarId(null);
    setFormData({ 
      academic_year: '2026-2027', 
      semester: 'Güz', 
      exam_type: 'Vize', 
      start_date: '', 
      end_date: '', 
      is_active: false 
    });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const openEditModal = (cal: AcademicCalendar) => {
    setIsEditing(true);
    setSelectedCalendarId(cal.calendar_id);
    setFormData({
      academic_year: cal.academic_year,
      semester: cal.semester,
      exam_type: cal.exam_type,
      start_date: cal.start_date,
      end_date: cal.end_date,
      is_active: cal.is_active
    });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    if (isSubmitting) return;
    setIsModalOpen(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setError(null);

      if (isEditing && selectedCalendarId) {
        const updateData: AcademicCalendarUpdateData = { ...formData };
        await updateAcademicCalendar(selectedCalendarId, updateData);
        setSuccessMsg('Akademik takvim başarıyla güncellendi.');
      } else {
        await createAcademicCalendar(formData);
        setSuccessMsg('Akademik takvim başarıyla eklendi.');
      }
      
      closeModal();
      fetchCalendars();
    } catch (err: any) {
      setError(err.message || 'İşlem sırasında bir hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (cal: AcademicCalendar) => {
    const isConfirmed = window.confirm(`Bu takvim kaydını silmek istediğinize emin misiniz?`);
    if (!isConfirmed) return;
    
    try {
      setError(null);
      setSuccessMsg(null);
      await deleteAcademicCalendar(cal.calendar_id);
      setSuccessMsg('Takvim başarıyla silindi.');
      fetchCalendars();
    } catch (err: any) {
      setError(`Silme işlemi başarısız: ${err.message}`);
    }
  };

  const handleToggleActive = async (cal: AcademicCalendar) => {
    try {
      setError(null);
      setSuccessMsg(null);
      await updateAcademicCalendar(cal.calendar_id, { is_active: !cal.is_active });
      setSuccessMsg(`Takvim durumu '${!cal.is_active ? 'Aktif' : 'Pasif'}' olarak güncellendi.`);
      fetchCalendars();
    } catch (err: any) {
      setError(`Durum güncellenemedi: ${err.message}`);
    }
  };

  return (
    <div className="calendars-page">
      <div className="page-header-desc">
        <p>Sınav dönemlerini yönetin, yeni akademik takvim ekleyin veya aktif olanları belirleyin.</p>
        <button className="btn-primary" onClick={openAddModal}>+ Yeni Takvim Ekle</button>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {error && !isModalOpen && <div className="alert-error">✕ {error}</div>}

      <div className="calendars-content">
        {loading && <div className="loading-state">Takvimler yükleniyor...</div>}
        
        {!loading && calendars.length === 0 && (
          <div className="empty-state">Sistemde henüz takvim bulunmuyor.</div>
        )}

        {!loading && calendars.length > 0 && (
          <div className="table-container">
            <table className="calendars-table">
              <thead>
                <tr>
                  <th>Yıl</th>
                  <th>Dönem</th>
                  <th>Sınav Türü</th>
                  <th>Başlangıç</th>
                  <th>Bitiş</th>
                  <th>Durum</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {calendars.map(cal => (
                  <tr key={cal.calendar_id} className={cal.is_active ? 'active-row' : ''}>
                    <td className="fw-600">{cal.academic_year}</td>
                    <td>{cal.semester}</td>
                    <td><span className="exam-type-badge">{cal.exam_type}</span></td>
                    <td>{cal.start_date}</td>
                    <td>{cal.end_date}</td>
                    <td>
                      <label className="toggle-switch">
                        <input 
                          type="checkbox" 
                          checked={cal.is_active} 
                          onChange={() => handleToggleActive(cal)}
                        />
                        <span className="slider round"></span>
                      </label>
                      <span className="toggle-label">{cal.is_active ? 'Aktif' : 'Pasif'}</span>
                    </td>
                    <td className="actions-cell">
                      <button className="btn-edit" onClick={() => openEditModal(cal)}>Düzenle</button>
                      <button className="btn-delete" onClick={() => handleDelete(cal)}>Sil</button>
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
              <h3>{isEditing ? 'Takvim Düzenle' : 'Yeni Takvim Ekle'}</h3>
              {!isSubmitting && (
                <button className="btn-close" onClick={closeModal}>×</button>
              )}
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && isModalOpen && <div className="alert-error">{error}</div>}

                <div className="form-group">
                  <label>Akademik Yıl</label>
                  <input 
                    type="text" 
                    value={formData.academic_year}
                    onChange={e => setFormData({...formData, academic_year: e.target.value})}
                    disabled={isSubmitting}
                    required
                    placeholder="Örn: 2026-2027"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Dönem</label>
                    <select 
                      value={formData.semester} 
                      onChange={e => setFormData({...formData, semester: e.target.value})}
                      disabled={isSubmitting}
                      required
                    >
                      <option value="Güz">Güz</option>
                      <option value="Bahar">Bahar</option>
                      <option value="Yaz">Yaz</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Sınav Türü</label>
                    <select 
                      value={formData.exam_type} 
                      onChange={e => setFormData({...formData, exam_type: e.target.value})}
                      disabled={isSubmitting}
                      required
                    >
                      <option value="Vize">Vize</option>
                      <option value="Final">Final</option>
                      <option value="Bütünleme">Bütünleme</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Başlangıç Tarihi</label>
                    <input 
                      type="date" 
                      value={formData.start_date}
                      onChange={e => setFormData({...formData, start_date: e.target.value})}
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Bitiş Tarihi</label>
                    <input 
                      type="date" 
                      value={formData.end_date}
                      onChange={e => setFormData({...formData, end_date: e.target.value})}
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="form-group checkbox-group">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={formData.is_active}
                      onChange={e => setFormData({...formData, is_active: e.target.checked})}
                      disabled={isSubmitting}
                    />
                    Bu takvimi sistemde varsayılan (Aktif) olarak kullan
                  </label>
                  <small className="text-muted" style={{display: 'block', marginTop: '4px'}}>
                    Eğer bu seçeneği işaretlerseniz, aynı sınav türüne ait diğer takvimler otomatik olarak pasif duruma geçecektir.
                  </small>
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

export default AcademicCalendarsPage;
