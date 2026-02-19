import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { PremiumButton, SpotlightCard, AnimatedText } from '../components/common';
import { DarkVeil } from '../components/backgrounds';

const Home: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) navigate('/feed');
  }, [isAuthenticated]);

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <DarkVeil
        speed={1.2}
        warpAmount={0.25}
      />

      <div className="text-center text-white max-w-4xl px-4 relative z-10 w-full">
        <AnimatedText
          text="Welcome to MoodShare"
          className="text-6xl font-black mb-6 text-white bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent"
          delay={0}
          animationType="fadeInUp"
        />

        <AnimatedText
          text="Connect with friends, share your thoughts, and discover what's happening in the world."
          className="text-xl mb-8 text-white/80 max-w-2xl mx-auto"
          delay={100}
          animationType="fadeInUp"
        />

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 delay-200">
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in" style={{ animationDelay: '200ms' }}>
            <Link to="/register">
              <button 
                className="group relative px-10 py-4 text-lg font-bold bg-gradient-to-r from-indigo-950 via-purple-900 to-indigo-950 text-white rounded-lg hover:scale-105 transition-transform shadow-lg shadow-purple-900/50 hover:shadow-purple-900/80 active:scale-95 border border-purple-800/50 hover:border-purple-700"
              >
                <span className="relative z-10">Create Account</span>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-purple-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
            </Link>
            <Link to="/login">
              <PremiumButton 
                size="lg" 
                variant="outline"
                className="group relative px-10 py-4 text-lg font-bold hover:scale-105 transition-transform hover:from-purple-500 hover:to-pink-500"
              >
                <span className="relative z-10">Sign In</span>
              </PremiumButton>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: '📝', title: 'Share Thoughts', desc: 'Express yourself and share your mood with friends' },
            { icon: '👥', title: 'Build Community', desc: 'Connect with like-minded people worldwide' },
            { icon: '💬', title: 'Engage', desc: 'Have meaningful conversations and discussions' },
          ].map((item, index) => (
            <div
              key={index}
              className="h-full transition-all duration-700 ease-out opacity-100 translate-y-0 hover:scale-105"
              style={{
                opacity: 1,
                transform: 'translateY(0)',
                animationDelay: `${300 + index * 100}ms`,
              }}
            >
              <SpotlightCard
                className="h-full p-8 flex flex-col items-center text-center hover:transform hover:scale-105 transition-transform duration-300"
                spotlightColor="rgba(168, 85, 247, 0.4)"
              >
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="text-xl font-bold mb-2 text-white">{item.title}</h3>
                <p className="text-white/70">{item.desc}</p>
              </SpotlightCard>
            </div>
          ))}
        </div>

        <div className="mt-16 pt-8 border-t border-white/10">
          <p className="text-white/60 text-sm">
            Join thousands of users already sharing their moods and connecting with the world
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;
