import { useEffect, useState } from 'react';
import { useCalendarStore } from '../store';
import { CalendarEventCard } from '../components/CalendarEventCard';
import { Loader2, Filter, CheckSquare, RefreshCw, ArrowLeft, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function CalendarEventListPage() {
    const navigate = useNavigate();
    const {
        events,
        fetchEvents,
        selectEvents,
        deselectEvents,
        loading,
        syncEvents,
        selectedCount,
        totalCount
    } = useCalendarStore();

    const [show1on1Only, setShow1on1Only] = useState(false);
    const [showSelectedOnly, setShowSelectedOnly] = useState(false);

    useEffect(() => {
        // Initial fetch
        fetchEvents({
            is_filtered: show1on1Only ? true : undefined,
            is_selected: showSelectedOnly ? true : undefined
        });
    }, [show1on1Only, showSelectedOnly, fetchEvents]);

    const handleToggleEvent = (id: number, isSelected: boolean) => {
        if (isSelected) {
            selectEvents([id]);
        } else {
            deselectEvents([id]);
        }
    };

    const handleSync = async () => {
        await syncEvents();
    };

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="p-2 -ml-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors"
                                title="뒤로 가기"
                            >
                                <ArrowLeft className="w-5 h-5" />
                            </button>
                            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                <Calendar className="w-6 h-6 text-indigo-600" />
                                캘린더 이벤트
                            </h1>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="text-sm text-slate-600 hidden sm:block">
                                총 <span className="font-semibold text-slate-900">{totalCount}</span>개 중
                                <span className="font-semibold text-indigo-600 ml-1">{selectedCount}</span>개 선택됨
                            </div>
                            <button
                                onClick={handleSync}
                                disabled={loading}
                                className="p-2 text-slate-400 hover:text-indigo-600 rounded-full hover:bg-indigo-50 transition-colors disabled:opacity-50"
                                title="동기화"
                            >
                                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Filters */}
                <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShow1on1Only(!show1on1Only)}
                            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${show1on1Only
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                                }`}
                        >
                            <Filter className="w-4 h-4 mr-2" />
                            1:1 미팅만 보기
                        </button>
                        <button
                            onClick={() => setShowSelectedOnly(!showSelectedOnly)}
                            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${showSelectedOnly
                                ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                                }`}
                        >
                            <CheckSquare className="w-4 h-4 mr-2" />
                            선택된 이벤트만 보기
                        </button>
                    </div>
                </div>

                {/* Event List */}
                {loading && events.length === 0 ? (
                    <div className="flex justify-center items-center h-64">
                        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                    </div>
                ) : events.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl border border-slate-200 shadow-sm">
                        <div className="mx-auto w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                            <Calendar className="w-6 h-6 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-900 mb-1">이벤트가 없습니다</h3>
                        <p className="text-slate-500">
                            {show1on1Only || showSelectedOnly ? '필터 조건을 변경해보세요.' : '캘린더를 동기화하거나 이벤트를 추가해주세요.'}
                        </p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {events.map((event) => (
                            <CalendarEventCard
                                key={event.id}
                                event={event}
                                onToggle={handleToggleEvent}
                            />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
