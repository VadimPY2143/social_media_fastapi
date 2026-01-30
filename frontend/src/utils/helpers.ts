import { formatDistanceToNow } from 'date-fns';

export const formatDate = (date: string | Date): string => {
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  } catch {
    return 'Unknown date';
  }
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length > maxLength) {
    return text.substring(0, maxLength) + '...';
  }
  return text;
};

export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();
};

export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const getErrorMessage = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An error occurred';
};

export const cn = (...classes: (string | boolean | undefined)[]): string => {
  return classes.filter((c) => typeof c === 'string').join(' ');
};
