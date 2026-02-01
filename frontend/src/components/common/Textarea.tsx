import React from 'react';
import { cn } from '../../utils/helpers';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-xs font-semibold text-white mb-3 uppercase tracking-wide">
            {label}
            {props.required && <span className="text-pink-300 ml-1">*</span>}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            'w-full px-4 py-3 bg-neutral-800/50 border rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 text-white placeholder-neutral-400 transition-all duration-200 backdrop-blur-sm resize-none',
            error ? 'border-pink-500/50 focus:ring-pink-500/50' : 'border-purple-500/20 hover:border-purple-500/40',
            className
          )}
          {...props}
        />
        {error && <p className="mt-2 text-xs text-pink-300 font-medium">{error}</p>}
        {helperText && !error && (
          <p className="mt-2 text-xs text-neutral-300">{helperText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Textarea;
