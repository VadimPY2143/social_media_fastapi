import React from 'react';
import { cn } from '../../utils/helpers';

interface GradientOrbProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  colors?: string[];
  size?: 'sm' | 'md' | 'lg' | 'xl';
  animation?: 'float' | 'pulse' | 'rotate';
}

const sizeMap = {
  sm: 'w-32 h-32',
  md: 'w-64 h-64',
  lg: 'w-96 h-96',
  xl: 'w-[500px] h-[500px]',
};

const animationMap = {
  float: 'animate-float',
  pulse: 'animate-pulse',
  rotate: 'animate-rotate',
};

const GradientOrb = React.forwardRef<HTMLDivElement, GradientOrbProps>(({
  className,
  colors = ['from-purple-500/20', 'to-pink-500/20'],
  size = 'md',
  animation = 'float',
  ...props
}, ref) => {
  return (
    <>
      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-30px);
          }
        }
        @keyframes rotate-slow {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-rotate {
          animation: rotate-slow 20s linear infinite;
        }
      `}</style>
      <div
        ref={ref}
        className={cn(
          'fixed rounded-full blur-3xl opacity-70 pointer-events-none',
          sizeMap[size],
          animationMap[animation],
          `bg-gradient-to-br ${colors.join(' ')}`,
          className
        )}
        {...props}
      />
    </>
  );
});

GradientOrb.displayName = 'GradientOrb';

export default GradientOrb;
