import React from 'react';
import './GlassIcons.css';
import { cn } from '../../utils/helpers';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactElement;
  label: string;
  color: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const colorMapping = {
  blue: 'rgba(59, 130, 246, 0.24)',
  purple: 'rgba(168, 85, 247, 0.24)',
  red: 'rgba(239, 68, 68, 0.24)',
  indigo: 'rgba(99, 102, 241, 0.24)',
  orange: 'rgba(249, 115, 22, 0.24)',
  green: 'rgba(34, 197, 94, 0.24)',
};

const sizeMap = {
  sm: 'text-xs px-3 py-1.5',
  md: 'text-sm px-4 py-2',
  lg: 'text-base px-6 py-3',
};

const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ icon, label, color, type = 'button', className, size = 'md', showLabel = true, ...props }, ref) => {
    const getBackgroundStyle = (color: string) => {
      if (colorMapping[color as keyof typeof colorMapping]) {
        return { background: colorMapping[color as keyof typeof colorMapping] };
      }
      return { background: 'rgba(255, 255, 255, 0.12)' };
    };

    // If icon is provided and no explicit showLabel, treat as icon button
    const isIconOnly = icon && !showLabel;

    if (isIconOnly) {
      // Icon-only glass button (original design)
      return (
        <button ref={ref} className={cn('icon-btn', className)} aria-label={label} type={type} {...props}>
          <span className="icon-btn__back" style={getBackgroundStyle(color)}></span>
          <span className="icon-btn__front">
            <span className="icon-btn__icon" aria-hidden="true">
              {icon}
            </span>
          </span>
          <span className="icon-btn__label">{label}</span>
        </button>
      );
    }

    // Text button with glass effect
    return (
      <button
        ref={ref}
        className={cn(
          'glass-btn',
          sizeMap[size],
          className
        )}
        type={type}
        {...props}
      >
        <span className="glass-btn__back" style={getBackgroundStyle(color)}></span>
        <span className="glass-btn__front">
          {icon && <span className="glass-btn__icon">{icon}</span>}
          <span>{label}</span>
        </span>
      </button>
    );
  }
);

GlassButton.displayName = 'GlassButton';

export default GlassButton;
