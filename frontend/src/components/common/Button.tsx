import React from 'react';
import GlassButton from './GlassButton';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  loading?: boolean;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      className,
      children,
      size = 'md',
      ...props
    },
    ref
  ) => {
    const colorMap = {
      primary: 'purple',
      secondary: 'blue',
      danger: 'red',
      ghost: 'indigo',
    };

    const label = React.Children.toArray(children).join('');

    return (
      <GlassButton
        ref={ref}
        label={label}
        color={colorMap[variant]}
        className={className}
        size={size}
        showLabel={true}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export default Button;
