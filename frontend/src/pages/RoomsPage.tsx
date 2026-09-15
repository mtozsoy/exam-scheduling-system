import React, { useState, useEffect } from 'react';
import { getRooms, createRoom, updateRoom, deleteRoom } from '../services/api';
import type { Room, RoomCreateData, RoomUpdateData } from '../types/rooms';
import './RoomsPage.css';

const RoomsPage: React.FC = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [selectedRoomCode, setSelectedRoomCode] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<RoomCreateData>({
    room_code: '',
    building: '',
    floor: 0,
    capacity: 0,
  });
  
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRooms();
      setRooms(data);
    } catch (err: any) {
      setError(err.message || 'Derslikler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setIsEditing(false);
    setSelectedRoomCode(null);
    setFormData({ room_code: '', building: '', floor: 0, capacity: 0 });
    setError(null);
    setSuccessMsg(null);
    setIsModalOpen(true);
  };

  const openEditModal = (room: Room) => {
    setIsEditing(true);
    setSelectedRoomCode(room.room_code);
    setFormData({
      room_code: room.room_code,
      building: room.building,
      floor: room.floor,
      capacity: room.capacity,
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

      if (isEditing && selectedRoomCode) {
        const updateData: RoomUpdateData = {
          building: formData.building,
          floor: formData.floor,
          capacity: formData.capacity,
        };
        await updateRoom(selectedRoomCode, updateData);
        setSuccessMsg('Derslik başarıyla güncellendi.');
      } else {
        await createRoom(formData);
        setSuccessMsg('Derslik başarıyla eklendi.');
      }
      
      closeModal();
      fetchRooms();
    } catch (err: any) {
      setError(err.message || 'İşlem sırasında bir hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (roomCode: string) => {
    const isConfirmed = window.confirm(`"${roomCode}" kodlu dersliği silmek istediğinize emin misiniz?`);
    if (!isConfirmed) return;
    
    try {
      setError(null);
      setSuccessMsg(null);
      await deleteRoom(roomCode);
      setSuccessMsg('Derslik başarıyla silindi.');
      fetchRooms();
    } catch (err: any) {
      setError(`Silme işlemi başarısız: ${err.message}`);
    }
  };

  return (
    <div className="rooms-page">
      <div className="page-header-desc">
        <p>Sistemdeki derslikleri görüntüleyin, yeni derslik ekleyin veya mevcut olanları düzenleyin.</p>
        <button className="btn-primary" onClick={openAddModal}>+ Yeni Derslik Ekle</button>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {error && !isModalOpen && <div className="alert-error">✕ {error}</div>}

      <div className="rooms-content">
        {loading && <div className="loading-state">Derslikler yükleniyor...</div>}
        
        {!loading && rooms.length === 0 && (
          <div className="empty-state">Sistemde henüz derslik bulunmuyor.</div>
        )}

        {!loading && rooms.length > 0 && (
          <div className="table-container">
            <table className="rooms-table">
              <thead>
                <tr>
                  <th>Derslik Kodu</th>
                  <th>Bina</th>
                  <th>Kat</th>
                  <th>Kapasite</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map(room => (
                  <tr key={room.room_code}>
                    <td className="fw-600">{room.room_code}</td>
                    <td>{room.building}</td>
                    <td>{room.floor}</td>
                    <td>{room.capacity}</td>
                    <td className="actions-cell">
                      <button 
                        className="btn-edit"
                        onClick={() => openEditModal(room)}
                      >
                        Düzenle
                      </button>
                      <button 
                        className="btn-delete"
                        onClick={() => handleDelete(room.room_code)}
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
              <h3>{isEditing ? 'Derslik Düzenle' : 'Yeni Derslik Ekle'}</h3>
              {!isSubmitting && (
                <button className="btn-close" onClick={closeModal}>×</button>
              )}
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && isModalOpen && <div className="alert-error">{error}</div>}

                <div className="form-group">
                  <label>Derslik Kodu</label>
                  <input 
                    type="text" 
                    value={formData.room_code}
                    onChange={e => setFormData({...formData, room_code: e.target.value})}
                    disabled={isEditing || isSubmitting}
                    required
                    placeholder="Örn: A101"
                  />
                  {isEditing && <small className="text-muted">Derslik kodu sonradan değiştirilemez.</small>}
                </div>

                <div className="form-group">
                  <label>Bina</label>
                  <input 
                    type="text" 
                    value={formData.building}
                    onChange={e => setFormData({...formData, building: e.target.value})}
                    disabled={isSubmitting}
                    required
                    placeholder="Örn: Mühendislik Binası"
                  />
                </div>

                <div className="form-group">
                  <label>Kat</label>
                  <input 
                    type="number" 
                    value={formData.floor}
                    onChange={e => setFormData({...formData, floor: parseInt(e.target.value) || 0})}
                    disabled={isSubmitting}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Kapasite</label>
                  <input 
                    type="number" 
                    value={formData.capacity}
                    onChange={e => setFormData({...formData, capacity: parseInt(e.target.value) || 0})}
                    disabled={isSubmitting}
                    required
                    min="1"
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

export default RoomsPage;
