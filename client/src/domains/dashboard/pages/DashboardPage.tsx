/**
 * Dashboard Page - 2026 Modern Design
 *
 * 원온원 미러 메인 대시보드
 */

import React from 'react';
import { useAuthStore } from '@/core/store/useAuthStore';
import { MainLayout } from '@/core/layout';
import {
  TrendingUp,
  Users,
  Target,
  Calendar,
  Sparkles,
  ArrowUpRight,
  MessageSquare,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/core/utils';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ElementType;
  colorClass: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  trend,
  icon: Icon,
  colorClass,
}) => {
  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200/60 shadow-soft hover:shadow-soft-lg transition-all duration-300 group">
      <div className="flex items-start justify-between mb-4">
        <div
          className={cn(
            'w-12 h-12 rounded-2xl flex items-center justify-center',
            colorClass
          )}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>
        <span
          className={cn(
            'text-sm font-semibold flex items-center gap-1',
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          )}
        >
          <ArrowUpRight className="w-4 h-4" />
          {change}
        </span>
      </div>
      <h3 className="text-sm font-medium text-slate-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
};

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <MainLayout>
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              안녕하세요, {user?.username || user?.name || '사용자'}님 👋
            </h1>
            <p className="text-slate-600">
              오늘도 성장하는 하루를 만들어보세요
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-200 shadow-soft hover:shadow-soft-lg">
            <Sparkles className="w-4 h-4" />
            AI 분석 시작
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="완료된 1:1 미팅"
          value="24"
          change="+12%"
          trend="up"
          icon={CheckCircle2}
          colorClass="bg-gradient-to-br from-primary-600 to-primary-700"
        />
        <StatCard
          title="활성 팀원"
          value="12"
          change="+3%"
          trend="up"
          icon={Users}
          colorClass="bg-gradient-to-br from-accent-500 to-accent-600"
        />
        <StatCard
          title="목표 달성률"
          value="87%"
          change="+5%"
          trend="up"
          icon={Target}
          colorClass="bg-gradient-to-br from-green-500 to-green-600"
        />
        <StatCard
          title="다음 미팅"
          value="3일 후"
          change="예정"
          trend="up"
          icon={Calendar}
          colorClass="bg-gradient-to-br from-orange-500 to-orange-600"
        />
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: AI 인사이트 - Large */}
        <div className="lg:col-span-2 bg-gradient-to-br from-primary-50 via-white to-accent-50 rounded-3xl p-8 border border-slate-200/60 shadow-soft hover:shadow-soft-lg transition-all duration-300">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-2">
                AI 인사이트
              </h2>
              <p className="text-slate-600">
                최근 미팅 데이터 기반 분석 결과
              </p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shadow-soft">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 border border-slate-200/60">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">
                    팀 커뮤니케이션 향상
                  </h3>
                  <p className="text-sm text-slate-600">
                    지난 달 대비 팀원들의 피드백 빈도가 32% 증가했습니다.
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 border border-slate-200/60">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-accent-100 flex items-center justify-center flex-shrink-0">
                  <MessageSquare className="w-4 h-4 text-accent-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">
                    개선 제안
                  </h3>
                  <p className="text-sm text-slate-600">
                    개발팀과의 정기 1:1 미팅 주기를 조정하는 것을 추천합니다.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: 다가오는 미팅 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/60 shadow-soft hover:shadow-soft-lg transition-all duration-300">
          <h2 className="text-lg font-bold text-slate-900 mb-4">
            다가오는 미팅
          </h2>
          <div className="space-y-3">
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center text-white font-semibold text-sm">
                  김
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-slate-900">김철수</p>
                  <p className="text-xs text-slate-500">Frontend Developer</p>
                  <p className="text-xs text-slate-600 mt-1">
                    12월 20일 14:00
                  </p>
                </div>
              </div>
            </div>
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center text-white font-semibold text-sm">
                  이
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-slate-900">이영희</p>
                  <p className="text-xs text-slate-500">Product Designer</p>
                  <p className="text-xs text-slate-600 mt-1">
                    12월 22일 10:00
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3: 최근 활동 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/60 shadow-soft hover:shadow-soft-lg transition-all duration-300">
          <h2 className="text-lg font-bold text-slate-900 mb-4">
            최근 활동
          </h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 pb-3 border-b border-slate-100">
              <div className="w-2 h-2 rounded-full bg-primary-500 mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">
                  미팅 기록 작성
                </p>
                <p className="text-xs text-slate-500">2시간 전</p>
              </div>
            </div>
            <div className="flex items-start gap-3 pb-3 border-b border-slate-100">
              <div className="w-2 h-2 rounded-full bg-accent-500 mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">
                  목표 업데이트
                </p>
                <p className="text-xs text-slate-500">5시간 전</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-green-500 mt-2" />
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">
                  AI 분석 완료
                </p>
                <p className="text-xs text-slate-500">1일 전</p>
              </div>
            </div>
          </div>
        </div>

        {/* Card 4: 팀 성과 - Large */}
        <div className="lg:col-span-2 bg-gradient-to-br from-slate-50 to-white rounded-3xl p-8 border border-slate-200/60 shadow-soft hover:shadow-soft-lg transition-all duration-300">
          <h2 className="text-xl font-bold text-slate-900 mb-6">
            팀 성과 개요
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-white rounded-2xl border border-slate-200/60">
              <p className="text-3xl font-bold text-primary-600 mb-1">92%</p>
              <p className="text-xs text-slate-600">목표 달성률</p>
            </div>
            <div className="text-center p-4 bg-white rounded-2xl border border-slate-200/60">
              <p className="text-3xl font-bold text-accent-600 mb-1">4.8</p>
              <p className="text-xs text-slate-600">평균 만족도</p>
            </div>
            <div className="text-center p-4 bg-white rounded-2xl border border-slate-200/60">
              <p className="text-3xl font-bold text-green-600 mb-1">156</p>
              <p className="text-xs text-slate-600">총 미팅 수</p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

