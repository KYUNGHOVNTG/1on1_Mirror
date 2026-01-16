import React from 'react';
import type { CalendarEvent } from '../types';
import { Users, MapPin, Calendar as CalendarIcon, Clock } from 'lucide-react';

interface CalendarEventCardProps {
    event: CalendarEvent;
    onToggle: (id: number, isSelected: boolean) => void;
}

export function CalendarEventCard({ event, onToggle }: CalendarEventCardProps) {
    const startDate = new Date(event.start_time);
    const endDate = new Date(event.end_time);

    const formattedDate = new Intl.DateTimeFormat('ko-KR', {
        month: 'long',
        day: 'numeric',
        weekday: 'short',
    }).format(startDate);

    const formattedTime = `${new Intl.DateTimeFormat('ko-KR', {
        hour: 'numeric',
        minute: 'numeric',
        hour12: false,
    }).format(startDate)} - ${new Intl.DateTimeFormat('ko-KR', {
        hour: 'numeric',
        minute: 'numeric',
        hour12: false,
    }).format(endDate)}`;

    const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onToggle(event.id, e.target.checked);
    };

    return (
        <div
            className={`relative group rounded-xl border p-5 transition-all duration-200 hover:shadow-md cursor-pointer
        ${event.is_selected
                    ? 'bg-indigo-50/50 border-indigo-200'
                    : 'bg-white border-slate-200 hover:border-indigo-100'
                }`}
            onClick={() => onToggle(event.id, !event.is_selected)}
        >
            <div className="flex items-start gap-4">
                {/* Checkbox */}
                <div className="pt-1 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                    <input
                        type="checkbox"
                        checked={event.is_selected}
                        onChange={handleCheckboxChange}
                        className="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                    />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                        <h3 className={`text-lg font-semibold truncate pr-4 ${event.is_selected ? 'text-indigo-900' : 'text-slate-900'}`}>
                            {event.summary}
                        </h3>
                        {event.is_filtered && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
                                1:1
                            </span>
                        )}
                    </div>

                    <div className="mt-3 space-y-2">
                        <div className="flex items-center text-sm text-slate-500">
                            <CalendarIcon className="w-4 h-4 mr-2 text-slate-400" />
                            <span>{formattedDate}</span>
                            <span className="mx-2 text-slate-300">|</span>
                            <Clock className="w-4 h-4 mr-2 text-slate-400" />
                            <span>{formattedTime}</span>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-slate-500">
                            <div className="flex items-center">
                                <Users className="w-4 h-4 mr-2 text-slate-400" />
                                <span>{event.attendees_count}명 참석</span>
                            </div>

                            {event.location && (
                                <div className="flex items-center truncate max-w-[200px]">
                                    <MapPin className="w-4 h-4 mr-2 text-slate-400 flex-shrink-0" />
                                    <span className="truncate">{event.location}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {event.description && (
                        <p className="mt-3 text-sm text-slate-500 line-clamp-2">
                            {event.description}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
