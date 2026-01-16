/**
 * Sidebar Component
 *
 * 2026 Modern Design 사이드바 네비게이션
 *
 * @example
 * <Sidebar isOpen={isOpen} onClose={handleClose} />
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Heart,
  History,
  Sparkles,
  Target,
  Settings,
  ChevronDown,
  Building2,
  User,
  X,
} from 'lucide-react';
import { cn } from '@/core/utils';
import { useAuthStore } from '@/core/store';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ElementType;
  path: string;
  badge?: string;
}

interface MenuGroup {
  id: string;
  label: string;
  items: MenuItem[];
}

const menuGroups: MenuGroup[] = [
  {
    id: 'overview',
    label: 'Overview',
    items: [
      { id: 'dashboard', label: '대시보드', icon: LayoutDashboard, path: '/dashboard' },
    ],
  },
  {
    id: 'preparation',
    label: 'Preparation',
    items: [
      { id: 'roleplay', label: 'AI 롤플레잉', icon: MessageSquare, path: '/roleplay' },
      { id: 'mindset', label: '마인드셋 체크', icon: Heart, path: '/mindset' },
    ],
  },
  {
    id: 'analysis',
    label: 'Analysis',
    items: [
      { id: 'history', label: '미팅 기록실', icon: History, path: '/history' },
      { id: 'insights', label: 'AI 인사이트', icon: Sparkles, path: '/insights' },
    ],
  },
  {
    id: 'strategy',
    label: 'Strategy',
    items: [
      { id: 'goals', label: '목표 관리', icon: Target, path: '/goals' },
    ],
  },
  {
    id: 'system',
    label: 'System',
    items: [
      { id: 'settings', label: '설정', icon: Settings, path: '/settings' },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();

  const handleNavigate = (path: string) => {
    navigate(path);
    if (onClose && window.innerWidth < 1024) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full w-[280px] bg-white',
          'border-r border-slate-200/60 shadow-soft',
          'backdrop-blur-md',
          'transition-transform duration-300 ease-in-out',
          'flex flex-col',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'lg:translate-x-0 lg:z-30'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shadow-soft">
              <span className="text-white font-bold text-lg">1:1</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900">1on1 Mirror</h1>
              <p className="text-xs text-slate-500">성과 관리 플랫폼</p>
            </div>
          </div>
          {/* Mobile Close Button */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {menuGroups.map((group) => (
            <div key={group.id} className="mb-6">
              <h3 className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {group.label}
              </h3>
              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNavigate(item.path)}
                      className={cn(
                        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl',
                        'text-sm font-medium transition-all duration-200',
                        'relative group',
                        isActive
                          ? 'bg-gradient-to-r from-primary-50 to-primary-100/50 text-primary-700'
                          : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                      )}
                    >
                      {/* Active Indicator */}
                      {isActive && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-primary-600 to-primary-700 rounded-r-full" />
                      )}

                      {/* Icon */}
                      <Icon
                        className={cn(
                          'w-5 h-5 transition-transform duration-200',
                          isActive ? 'text-primary-600' : 'text-slate-500',
                          'group-hover:scale-110'
                        )}
                      />

                      {/* Label */}
                      <span className="flex-1 text-left">{item.label}</span>

                      {/* Badge */}
                      {item.badge && (
                        <span className="px-2 py-0.5 text-xs font-semibold bg-accent-100 text-accent-700 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* User Profile & Workspace Switcher */}
        <div className="p-4 border-t border-slate-200/60 bg-slate-50/50">
          <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white transition-all duration-200 group">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center shadow-soft">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 text-left">
              <p className="text-sm font-semibold text-slate-900">
                {user?.username || '사용자'}
              </p>
              <p className="text-xs text-slate-500 flex items-center gap-1">
                <Building2 className="w-3 h-3" />
                My Workspace
              </p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
          </button>
        </div>
      </aside>
    </>
  );
};
