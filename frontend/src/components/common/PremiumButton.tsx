import React from 'react';
import { cn } from '../../utils/helpers';

interface PremiumButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'gradient' | 'outline' | 'accent' | 'danger';
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
      'inline-flex items-center justify-center font-semibold transition-all duration-200 rounded-lg border shadow-sm shadow-white/5 backdrop-blur-sm disabled:opacity-50 disabled:cursor-not-allowed';

    const sizeStyles = {
      sm: 'px-4 py-2 text-sm',
      md: 'px-6 py-2.5 text-sm',
      lg: 'px-8 py-3 text-base',
    };

    const variantStyles = {
      primary:
        'bg-white/15 text-white border-white/30 hover:bg-white/25 hover:border-white/40 active:scale-95',
      secondary:
        'bg-neutral-800/70 text-white border-white/20 hover:bg-neutral-700/80 hover:border-white/35 active:scale-95',
      gradient:
        'bg-neutral-900/70 text-white border-white/25 hover:bg-neutral-800/80 hover:border-white/40 active:scale-95',
      ghost:
        'bg-transparent text-white border-white/25 hover:border-white/40 hover:bg-white/5 active:scale-95',
      outline:
        'bg-transparent text-white border-white/35 hover:bg-white/7 active:scale-95',
      accent:
        'bg-sky-400/80 text-slate-950 border-white/40 hover:bg-sky-300/90 hover:border-white/60 active:scale-95',
      danger:
        'bg-red-500/80 text-white border-white/40 hover:bg-red-400/90 hover:border-white/60 active:scale-95',
    };

    const roundedStyles = 'rounded-lg';

    return (
      <button
        ref={ref}
        className={cn(baseStyles, sizeStyles[size], variantStyles[variant], roundedStyles, className)}
        disabled={disabled || loading}
        {...props}
      >
        {/* Loading spinner */}
        {loading && <span className="inline-block mr-2 w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>}

        {/* Icon */}
        {icon && <span className="mr-2 flex items-center justify-center">{icon}</span>}

        {/* Text */}
        <span className="relative z-10">{children}</span>

      </button>
    );
  }
);

PremiumButton.displayName = 'PremiumButton';

export default PremiumButton;
