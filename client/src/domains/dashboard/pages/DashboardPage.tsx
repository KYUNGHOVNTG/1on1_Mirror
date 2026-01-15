import React from 'react';
import { useAuthStore } from '../../../core/store/useAuthStore';
import { useNavigate } from 'react-router-dom';
import { checkDatabaseConnection } from '../../system/api';
import { Database } from 'lucide-react';

export const DashboardPage: React.FC = () => {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleDbCheck = async () => {
        try {
            const result = await checkDatabaseConnection();
            alert(`✅ DB 연결 성공!\n\n${result.message}`);
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : 'DB 연결 실패';
            alert(`❌ DB 연결 실패\n\n${errorMessage}`);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h1 className="text-xl font-bold text-slate-800">1on1 Mirror Dashboard</h1>
                <div className="flex items-center gap-4">
                    {user && (
                        <div className="flex items-center gap-2">
                            {user.picture && (
                                <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                            )}
                            <span className="text-sm font-medium text-slate-600">{user.name}</span>
                        </div>
                    )}
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        로그아웃
                    </button>
                </div>
            </header>

            <main className="p-8">
                <div className="max-w-7xl mx-auto">
                    <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                        <p className="text-slate-500 mb-6">대시보드 준비 중입니다.</p>

                        <button
                            onClick={handleDbCheck}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:bg-primary/90 transition-colors"
                        >
                            <Database size={18} />
                            DB 연결 테스트
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

