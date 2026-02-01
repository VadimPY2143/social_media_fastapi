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

const gradientMapping = {
  blue: 'linear-gradient(hsl(223, 90%, 50%), hsl(208, 90%, 50%))',
  purple: 'linear-gradient(hsl(283, 90%, 50%), hsl(268, 90%, 50%))',
  red: 'linear-gradient(hsl(3, 90%, 50%), hsl(348, 90%, 50%))',
  indigo: 'linear-gradient(hsl(253, 90%, 50%), hsl(238, 90%, 50%))',
  orange: 'linear-gradient(hsl(43, 90%, 50%), hsl(28, 90%, 50%))',
  green: 'linear-gradient(hsl(123, 90%, 40%), hsl(108, 90%, 40%))'
};

const sizeMap = {
  sm: 'text-xs px-3 py-1.5',
  md: 'text-sm px-4 py-2',
  lg: 'text-base px-6 py-3',
};

const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ icon, label, color, type = 'button', className, size = 'md', showLabel = true, ...props }, ref) => {
    const getBackgroundStyle = (color: string) => {
      if (gradientMapping[color as keyof typeof gradientMapping]) {
        return { background: gradientMapping[color as keyof typeof gradientMapping] };
      }
      return { background: color };
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
