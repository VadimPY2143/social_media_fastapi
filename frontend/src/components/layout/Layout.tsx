import React from 'react';
import Header from './Header';
import Notification from '../common/Notification';
import { DarkVeil } from '../backgrounds';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen relative">
      <DarkVeil
        speed={1.2}
        warpAmount={0.25}
      />
      <div className="relative z-10">
        <Header />
        <main className="max-w-6xl mx-auto px-4 py-10">
          {children}
        </main>
        <Notification />
      </div>
    </div>
  );
};

export default Layout;
