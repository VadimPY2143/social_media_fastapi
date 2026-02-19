import React from 'react';
import { cn } from '../../utils/helpers';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className={cn('bg-neutral-900 rounded-xl border border-white/10 shadow-2xl shadow-black/40 w-full', sizeClasses[size])}>
        {title && (
          <div className="flex items-center justify-between p-5 border-b border-white/10">
            <h2 className="text-lg font-semibold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="text-white/60 hover:text-white text-2xl font-bold"
            >
              ×
            </button>
          </div>
        )}
        <div className="p-5 text-white">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
