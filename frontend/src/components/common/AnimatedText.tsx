import React, { useEffect, useState } from 'react';

interface AnimatedTextProps extends React.HTMLAttributes<HTMLDivElement> {
  text: string;
  className?: string;
  delay?: number;
  animationType?: 'fadeInUp' | 'slideInLeft' | 'scaleIn';
}

const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  className = '',
  delay = 0,
  animationType = 'fadeInUp',
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const animationStyles = {
    fadeInUp: isVisible
      ? 'opacity-100 translate-y-0'
      : 'opacity-0 translate-y-10',
    slideInLeft: isVisible
      ? 'opacity-100 translate-x-0'
      : 'opacity-0 -translate-x-10',
    scaleIn: isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95',
  };

  return (
    <div
      className={`transition-all duration-700 ease-out ${animationStyles[animationType]} ${className}`}
    >
      {text}
    </div>
  );
};

export default AnimatedText;
