import React, { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser } from '../services/api';
import type { User, UserUpdateData } from '../services/api';

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  
  // Form state
  const [isEditing, setIsEditing] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('secretary');

  const currentUsername = localStorage.getItem('username');

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Kullanıcılar yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openAddModal = () => {
    setIsEditing(false);
    setEditId(null);
    setUsername('');
    setPassword('');
    setRole('secretary');
    setError(null);
    setSuccessMsg(null);
    setShowModal(true);
  };

  const openEditModal = (user: User) => {
    setIsEditing(true);
    setEditId(user.KullaniciID);
    setUsername(user.KullaniciAdi);
    setPassword(''); // Edit modunda şifre boş başlar (sadece değişecekse girilir)
    setRole(user.Rol);
    setError(null);
    setSuccessMsg(null);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setError(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
        if (isEditing && editId !== null) {
          const updateData: UserUpdateData = { username, role };
          if (password.trim() !== '') {
            updateData.password = password;
          }
          await updateUser(editId, updateData);
          setSuccessMsg('Kullanıcı başarıyla güncellendi.');
        } else {
          await createUser({ username, password, role });
          setSuccessMsg('Kullanıcı başarıyla eklendi.');
        }
        closeModal();
        fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Bir hata oluştu.');
    }
  };

  const handleDelete = async (user: User) => {
    if (user.KullaniciAdi === currentUsername) {
      setError("Kendi hesabınızı silemezsiniz.");
      return;
    }
    if (window.confirm(`"${user.KullaniciAdi}" kullanıcısını silmek istediğinize emin misiniz?`)) {
      try {
        await deleteUser(user.KullaniciID);
        setSuccessMsg('Kullanıcı başarıyla silindi.');
        fetchUsers();
      } catch (err: any) {
        setError(err.message || 'Silme işlemi başarısız.');
      }
    }
  };

  return (
    <div className="page-container">
      <div className="page-header-desc">
        <p>Sistemdeki kullanıcıları yönetin, yeni yetkili ekleyin veya düzenleyin.</p>
        <button className="btn-primary" onClick={openAddModal}>+ Yeni Kullanıcı Ekle</button>
      </div>

      {successMsg && <div className="alert-success">✓ {successMsg}</div>}
      {loading && <p>Yükleniyor...</p>}
      {error && !showModal && <div className="alert-error">✕ {error}</div>}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Kullanıcı Adı</th>
              <th>Rol</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.KullaniciID}>
                <td>{user.KullaniciID}</td>
                <td>{user.KullaniciAdi}</td>
                <td>
                  <span className={`status-badge ${user.Rol === 'admin' ? 'active' : 'inactive'}`}>
                    {user.Rol === 'admin' ? 'Admin' : 'Sekreter'}
                  </span>
                </td>
                <td>
                  <div className="actions-cell">
                    <button className="btn-edit" onClick={() => openEditModal(user)}>Düzenle</button>
                    {user.KullaniciAdi !== currentUsername && (
                      <button className="btn-delete" onClick={() => handleDelete(user)}>Sil</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {users.length === 0 && !loading && (
              <tr>
                <td colSpan={4} className="text-center">Kullanıcı bulunamadı.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{isEditing ? 'Kullanıcıyı Düzenle' : 'Yeni Kullanıcı Ekle'}</h3>
              <button className="btn-close" onClick={closeModal}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && <div className="alert-error">{error}</div>}
              <div className="form-group">
                <label>Kullanıcı Adı</label>
                <input 
                  type="text" 
                  value={username} 
                  onChange={e => setUsername(e.target.value)} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>{isEditing ? 'Yeni Şifre (Boş bırakılabilir)' : 'Şifre'}</label>
                <input 
                  type="password" 
                  value={password} 
                  onChange={e => setPassword(e.target.value)} 
                  required={!isEditing} 
                />
              </div>
              <div className="form-group">
                <label>Rol</label>
                <select value={role} onChange={e => setRole(e.target.value)}>
                  <option value="secretary">Sekreter</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={closeModal}>İptal</button>
                <button type="submit" className="btn-primary">Kaydet</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
