import React from 'react';
import { cn } from '../../utils/helpers';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      className,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseClasses = 'font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-neutral-950 text-sm uppercase tracking-wide';
    
    const variantClasses = {
      primary: 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 shadow-xl hover:shadow-pink-500/30 focus:ring-purple-400',
      secondary: 'bg-neutral-800/70 border border-purple-500/30 text-white hover:bg-neutral-700/70 hover:border-purple-500/60 shadow-lg focus:ring-purple-500',
      danger: 'bg-gradient-to-r from-pink-600 to-red-600 text-white hover:from-pink-500 hover:to-red-500 shadow-xl hover:shadow-pink-500/30 focus:ring-pink-400',
      ghost: 'bg-transparent text-white hover:bg-purple-500/10 hover:text-purple-300 focus:ring-purple-500',
    };

    const sizeClasses = {
      sm: 'px-3 py-1 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    const disabledClasses = disabled || loading ? 'opacity-50 cursor-not-allowed' : '';

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          disabledClasses,
          className
        )}
        {...props}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-current border-r-transparent rounded-full animate-spin" />
            Loading...
          </span>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
