import React from 'react';
import type { Proposal } from '../types/scheduling';
import './ProposalCard.css';

interface ProposalCardProps {
  proposal: Proposal;
  isConfirming: boolean;
  isConfirmed: boolean;
  confirmError: string | null;
  onConfirm: () => void;
}

const ProposalCard: React.FC<ProposalCardProps> = ({
  proposal,
  isConfirming,
  isConfirmed,
  confirmError,
  onConfirm
}) => {
  return (
    <div className={`proposal-card ${isConfirmed ? 'confirmed' : ''}`}>
      <div className="proposal-card-header">
        <div className="datetime">
          <div className="date">{proposal.date}</div>
          <div className="time">
            {proposal.start_time} - {proposal.end_time}
          </div>
        </div>
        <div className="student-count">
          Toplam Öğrenci: {proposal.total_students}
        </div>
      </div>

      <div className="proposal-card-body">
        <h4>Atanan Derslikler ({proposal.rooms.length})</h4>
        {proposal.rooms.length === 0 ? (
          <p className="no-rooms-msg">Bu sınav için derslik atamasına gerek duyulmadı.</p>
        ) : (
          <div className="room-grid">
            {proposal.rooms.map((room, idx) => (
              <div key={idx} className="room-item">
                <div className="room-code">{room.room_code}</div>
                <div className="room-details">
                  <span>Kapasite: {room.capacity}</span>
                  <span>Atanan: {room.assigned_count}</span>
                  {room.invigilator_id && (
                    <span className="invigilator">
                      Gözetmen ID: {room.invigilator_id}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {confirmError && <div className="alert-error" style={{marginTop: '20px'}}>{confirmError}</div>}
      {isConfirmed && <div className="alert-success" style={{marginTop: '20px'}}>✓ Sınav başarıyla onaylandı ve kaydedildi!</div>}

      <div className="proposal-card-footer">
        <button
          className={`btn-primary confirm-btn ${isConfirmed ? 'success-btn' : ''}`}
          onClick={onConfirm}
          disabled={isConfirming || isConfirmed}
        >
          {isConfirming
            ? 'Onaylanıyor...'
            : isConfirmed
            ? '✓ Onaylandı'
            : 'Bu Planı Onayla'}
        </button>
      </div>
    </div>
  );
};

export default ProposalCard;
