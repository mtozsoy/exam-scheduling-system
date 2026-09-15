import React, { useState, useEffect } from 'react';
import { getInvigilators, createInvigilator, updateInvigilator, deleteInvigilator } from '../services/api';
import type { Invigilator, InvigilatorCreateData, InvigilatorUpdateData } from '../types/invigilators';
import './InvigilatorsPage.css';

const InvigilatorsPage: React.FC = () => {
  const [invigilators, setInvigilators] = useState<Invigilator[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [selectedInvigilatorId, setSelectedInvigilatorId] = useState<number | null>(null);
  
  const [formData, setFormData] = useState<InvigilatorCreateData>({
    first_name: '',
    last_name: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    fetchInvigilators();
  }, []);

  const fetchInvigilators = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getInvigilators();
      setInvigilators(data);
    } catch (err: any) {
      setError(err.message || 'Gözetmenler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setIsEditing(false);
    setSelectedInvigilatorId(null);
    setFormData({ first_name: '', last_name: '' });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const openEditModal = (invigilator: Invigilator) => {
    setIsEditing(true);
    setSelectedInvigilatorId(invigilator.invigilator_id);
    setFormData({
      first_name: invigilator.first_name,
      last_name: invigilator.last_name
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

      if (isEditing && selectedInvigilatorId) {
        const updateData: InvigilatorUpdateData = {
          first_name: formData.first_name,
          last_name: formData.last_name
        };
        await updateInvigilator(selectedInvigilatorId, updateData);
        setSuccessMsg('Gözetmen başarıyla güncellendi.');
      } else {
        await createInvigilator(formData);
        setSuccessMsg('Gözetmen başarıyla eklendi.');
      }
      
      closeModal();
      fetchInvigilators();
    } catch (err: any) {
      setError(err.message || 'İşlem sırasında bir hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (invigilator: Invigilator) => {
    const isConfirmed = window.confirm(`"${invigilator.first_name} ${invigilator.last_name}" isimli gözetmeni silmek istediğinize emin misiniz?`);
    if (!isConfirmed) return;
    
    try {
      setError(null);
      setSuccessMsg(null);
      await deleteInvigilator(invigilator.invigilator_id);
      setSuccessMsg('Gözetmen başarıyla silindi.');
      fetchInvigilators();
    } catch (err: any) {
      setError(`Silme işlemi başarısız: ${err.message}`);
    }
  };

  return (
    <div className="invigilators-page">
      <div className="page-header-desc">
        <p>Sistemdeki gözetmenleri görüntüleyin, yeni gözetmen ekleyin veya mevcut olanları düzenleyin.</p>
        <button className="btn-primary" onClick={openAddModal}>+ Yeni Gözetmen Ekle</button>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {error && !isModalOpen && <div className="alert-error">✕ {error}</div>}

      <div className="invigilators-content">
        {loading && <div className="loading-state">Gözetmenler yükleniyor...</div>}
        
        {!loading && invigilators.length === 0 && (
          <div className="empty-state">Sistemde henüz gözetmen bulunmuyor.</div>
        )}

        {!loading && invigilators.length > 0 && (
          <div className="table-container">
            <table className="invigilators-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Ad</th>
                  <th>Soyad</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {invigilators.map(invigilator => (
                  <tr key={invigilator.invigilator_id}>
                    <td className="fw-600">{invigilator.invigilator_id}</td>
                    <td>{invigilator.first_name}</td>
                    <td>{invigilator.last_name}</td>
                    <td className="actions-cell">
                      <button 
                        className="btn-edit"
                        onClick={() => openEditModal(invigilator)}
                      >
                        Düzenle
                      </button>
                      <button 
                        className="btn-delete"
                        onClick={() => handleDelete(invigilator)}
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
              <h3>{isEditing ? 'Gözetmen Düzenle' : 'Yeni Gözetmen Ekle'}</h3>
              {!isSubmitting && (
                <button className="btn-close" onClick={closeModal}>×</button>
              )}
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && isModalOpen && <div className="alert-error">{error}</div>}

                {isEditing && (
                  <div className="form-group">
                    <label>Gözetmen ID</label>
                    <input 
                      type="text" 
                      value={selectedInvigilatorId || ''}
                      disabled
                    />
                    <small className="text-muted">ID numarası otomatik atanır ve değiştirilemez.</small>
                  </div>
                )}

                <div className="form-group">
                  <label>Ad</label>
                  <input 
                    type="text" 
                    value={formData.first_name}
                    onChange={e => setFormData({...formData, first_name: e.target.value})}
                    disabled={isSubmitting}
                    required
                    placeholder="Örn: Ahmet"
                  />
                </div>

                <div className="form-group">
                  <label>Soyad</label>
                  <input 
                    type="text" 
                    value={formData.last_name}
                    onChange={e => setFormData({...formData, last_name: e.target.value})}
                    disabled={isSubmitting}
                    required
                    placeholder="Örn: Yılmaz"
                  />
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

export default InvigilatorsPage;
