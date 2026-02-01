import React from 'react';
import { cn } from '../../utils/helpers';

interface PremiumButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'gradient' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
}

const PremiumButton = React.forwardRef<HTMLButtonElement, PremiumButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      icon,
      loading = false,
      disabled = false,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'relative inline-flex items-center justify-center font-semibold transition-all duration-300 overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed';

    const sizeStyles = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-2.5 text-sm',
      lg: 'px-8 py-3 text-base',
    };

    const variantStyles = {
      primary:
        'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/50 hover:shadow-purple-500/80 hover:from-purple-500 hover:to-purple-400 active:scale-95',
      secondary:
        'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/50 hover:shadow-blue-500/80 hover:from-blue-500 hover:to-blue-400 active:scale-95',
      gradient:
        'bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 text-white shadow-lg shadow-purple-500/50 hover:shadow-purple-500/80 hover:shadow-2xl active:scale-95',
      ghost:
        'bg-transparent text-white border border-white/20 hover:border-white/40 hover:bg-white/5 active:scale-95',
      outline:
        'bg-transparent text-white border-2 border-gradient-r from-purple-500 to-pink-500 hover:bg-white/5 active:scale-95',
    };

    const roundedStyles = 'rounded-lg';

    return (
      <button
        ref={ref}
        className={cn(baseStyles, sizeStyles[size], variantStyles[variant], roundedStyles, className)}
        disabled={disabled || loading}
        {...props}
      >
        {/* Shimmer effect for certain variants */}
        {(variant === 'primary' || variant === 'secondary' || variant === 'gradient') && (
          <div className="absolute inset-0 -top-1 h-full w-full bg-gradient-to-b from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        )}

        {/* Loading spinner */}
        {loading && <span className="inline-block mr-2 w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>}

        {/* Icon */}
        {icon && <span className="mr-2 flex items-center justify-center">{icon}</span>}

        {/* Text */}
        <span className="relative z-10">{children}</span>

        {/* Hover glow effect */}
        <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600/0 via-purple-500/0 to-pink-600/0 rounded-lg blur opacity-0 group-hover:opacity-75 transition-opacity duration-300 -z-10"></div>
      </button>
    );
  }
);

PremiumButton.displayName = 'PremiumButton';

export default PremiumButton;
