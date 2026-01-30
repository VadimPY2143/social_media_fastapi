import React from 'react';
import Header from './Header';
import Notification from '../common/Notification';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-950 via-purple-950 to-neutral-950">
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>
      </div>
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-10">
        {children}
      </main>
      <Notification />
    </div>
  );
};

export default Layout;
