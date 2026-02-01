import React, { useRef, useState } from 'react';
import { cn } from '../../utils/helpers';

interface SpotlightCardProps {
  children: React.ReactNode;
  className?: string;
  spotlightColor?: string;
}

const SpotlightCard = React.forwardRef<HTMLDivElement, SpotlightCardProps>(
  ({ children, className, spotlightColor = 'rgba(168, 85, 247, 0.3)' }, ref) => {
    const divRef = useRef<HTMLDivElement>(null);
    const [isMounted, setIsMounted] = useState(false);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [opacity, setOpacity] = useState(0);

    React.useEffect(() => {
      setIsMounted(true);
    }, []);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
      if (!divRef.current || !isMounted) return;

      const div = divRef.current;
      const rect = div.getBoundingClientRect();

      setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      setOpacity(1);
    };

    const handleMouseLeave = () => {
      setOpacity(0);
    };

    return (
      <div
        ref={divRef || ref}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className={cn(
          'relative group rounded-xl border border-white/10 bg-gradient-to-br from-neutral-900/50 to-neutral-950/50 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-white/20',
          className
        )}
      >
        {/* Spotlight effect */}
        <div
          className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition-opacity duration-300"
          style={{
            opacity: opacity,
            background: `radial-gradient(600px at ${position.x}px ${position.y}px, ${spotlightColor}, transparent 80%)`,
          }}
        />

        {/* Content */}
        <div className="relative z-10">{children}</div>
      </div>
    );
  }
);

SpotlightCard.displayName = 'SpotlightCard';

export default SpotlightCard;
