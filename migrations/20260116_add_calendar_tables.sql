-- ====================
-- 구글 캘린더 연동 테이블 추가
-- 생성일: 2026-01-16
-- 설명: 구글 캘린더 연동, 이벤트 동기화, 이벤트 선택 기능을 위한 테이블
-- ====================

-- 1. calendar_connections: 사용자별 구글 캘린더 연동 정보
CREATE TABLE IF NOT EXISTS calendar_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    google_calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMPTZ NOT NULL,
    channel_id VARCHAR(255),
    resource_id VARCHAR(255),
    webhook_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, google_calendar_id)
);
CREATE INDEX IF NOT EXISTS ix_calendar_connections_user_id ON calendar_connections(user_id);
CREATE INDEX IF NOT EXISTS ix_calendar_connections_is_active ON calendar_connections(is_active);

-- 2. calendar_events: 동기화된 캘린더 이벤트
CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    calendar_connection_id INTEGER NOT NULL REFERENCES calendar_connections(id) ON DELETE CASCADE,
    google_event_id VARCHAR(255) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    attendees_count INTEGER DEFAULT 0,
    attendees_emails JSONB DEFAULT '[]'::jsonb,
    location VARCHAR(500),
    is_filtered BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(calendar_connection_id, google_event_id)
);
CREATE INDEX IF NOT EXISTS ix_calendar_events_connection_id ON calendar_events(calendar_connection_id);
CREATE INDEX IF NOT EXISTS ix_calendar_events_google_event_id ON calendar_events(google_event_id);
CREATE INDEX IF NOT EXISTS ix_calendar_events_start_time ON calendar_events(start_time);
CREATE INDEX IF NOT EXISTS ix_calendar_events_is_filtered ON calendar_events(is_filtered);
CREATE INDEX IF NOT EXISTS ix_calendar_events_is_selected ON calendar_events(is_selected);

-- 3. calendar_event_selections: 선택된 이벤트와 1:1 세션 연결
CREATE TABLE IF NOT EXISTS calendar_event_selections (
    id SERIAL PRIMARY KEY,
    calendar_event_id INTEGER NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    one_on_one_session_id INTEGER REFERENCES one_on_one_sessions(id) ON DELETE SET NULL,
    selected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(calendar_event_id)
);
CREATE INDEX IF NOT EXISTS ix_calendar_event_selections_event_id ON calendar_event_selections(calendar_event_id);
CREATE INDEX IF NOT EXISTS ix_calendar_event_selections_session_id ON calendar_event_selections(one_on_one_session_id);

-- ====================
-- 롤백 SQL (문제 발생 시 실행)
-- ====================
-- DROP TABLE IF EXISTS calendar_event_selections CASCADE;
-- DROP TABLE IF EXISTS calendar_events CASCADE;
-- DROP TABLE IF EXISTS calendar_connections CASCADE;
