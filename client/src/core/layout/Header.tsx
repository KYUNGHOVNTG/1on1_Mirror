/**
 * Header Component
 *
 * 2026 Modern Design 상단 헤더
 *
 * @example
 * <Header onMenuClick={handleMenuClick} />
 */

import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Search, Bell, Sparkles, Command } from 'lucide-react';
import { cn } from '@/core/utils';

interface HeaderProps {
  onMenuClick?: () => void;
}

// Breadcrumb 매핑
const breadcrumbMap: Record<string, { label: string; parent?: string }> = {
  '/dashboard': { label: '대시보드' },
  '/roleplay': { label: 'AI 롤플레잉', parent: 'Preparation' },
  '/mindset': { label: '마인드셋 체크', parent: 'Preparation' },
  '/history': { label: '미팅 기록실', parent: 'Analysis' },
  '/insights': { label: 'AI 인사이트', parent: 'Analysis' },
  '/goals': { label: '목표 관리', parent: 'Strategy' },
  '/settings': { label: '설정', parent: 'System' },
};

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const location = useLocation();
  const [hasNotification, setHasNotification] = useState(true);
  const [aiStatus, setAiStatus] = useState<'active' | 'idle'>('active');

  const currentPage = breadcrumbMap[location.pathname] || { label: '홈' };

  return (
    <header
      className={cn(
        'sticky top-0 z-20 h-16 bg-white/80 backdrop-blur-md',
        'border-b border-slate-200/60 shadow-soft'
      )}
    >
      <div className="h-full max-w-full px-4 lg:px-6 flex items-center justify-between gap-4">
        {/* Left Section: Menu Button (Mobile) + Breadcrumb */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-slate-700" />
          </button>

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm">
            {currentPage.parent && (
              <>
                <span className="text-slate-500 font-medium">{currentPage.parent}</span>
                <span className="text-slate-300">/</span>
              </>
            )}
            <span className="text-slate-900 font-semibold">{currentPage.label}</span>
          </div>
        </div>

        {/* Right Section: Search + Notifications + AI Status */}
        <div className="flex items-center gap-3">
          {/* Search Bar */}
          <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-200/60 transition-colors group min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
            <input
              type="text"
              placeholder="검색..."
              className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-500 outline-none"
            />
            <kbd className="hidden lg:flex items-center gap-0.5 px-1.5 py-0.5 text-xs font-semibold text-slate-500 bg-white border border-slate-200 rounded">
              <Command className="w-3 h-3" />
              K
            </kbd>
          </div>

          {/* Mobile Search Button */}
          <button className="md:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors">
            <Search className="w-5 h-5 text-slate-600" />
          </button>

          {/* AI Status Indicator */}
          <button
            onClick={() => setAiStatus(aiStatus === 'active' ? 'idle' : 'active')}
            className={cn(
              'hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl transition-all duration-200',
              aiStatus === 'active'
                ? 'bg-gradient-to-r from-primary-50 to-primary-100/50 text-primary-700 hover:from-primary-100 hover:to-primary-200/50'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            )}
          >
            <Sparkles
              className={cn(
                'w-4 h-4',
                aiStatus === 'active' && 'animate-pulse'
              )}
            />
            <span className="text-xs font-semibold">
              {aiStatus === 'active' ? 'AI 활성' : 'AI 대기'}
            </span>
          </button>

          {/* Notifications */}
          <button
            onClick={() => setHasNotification(false)}
            className="relative p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <Bell className="w-5 h-5 text-slate-600" />
            {hasNotification && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent-500 rounded-full animate-pulse" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
