import React from 'react';
import { cn } from '../../utils/helpers';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'bg-neutral-900/50 backdrop-blur-xl rounded-2xl border border-purple-500/20 shadow-2xl hover:shadow-2xl hover:shadow-purple-500/20 hover:border-purple-500/40 transition-all duration-300 p-6',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);

Card.displayName = 'Card';

export default Card;
