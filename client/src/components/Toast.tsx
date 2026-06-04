import React from 'react';
import { useAuth } from '../context/AuthContext';
import { CheckCircle, AlertTriangle } from 'lucide-react';

const Toast: React.FC = () => {
  const { toast } = useAuth();

  if (!toast.show) return null;

  return (
    <div className="toast-container">
      <div className={`toast toast-${toast.type}`}>
        {toast.type === 'success' ? (
          <CheckCircle size={18} />
        ) : (
          <AlertTriangle size={18} />
        )}
        <span>{toast.message}</span>
      </div>
    </div>
  );
};

export default Toast;
