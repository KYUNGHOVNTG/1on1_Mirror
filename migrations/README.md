# Database Migrations

이 폴더는 데이터베이스 스키마 변경 이력을 관리합니다.

## 명명 규칙

```
YYYYMMDD_description.sql
```

예시:
- `20260116_add_refresh_token_to_users.sql`
- `20260120_create_sessions_table.sql`

## 마이그레이션 파일 구조

```sql
-- 변경 설명
-- 작성자: [이름]
-- 작성일: YYYY-MM-DD

-- 변경 사항 적용
ALTER TABLE users
ADD COLUMN new_column VARCHAR(100);

-- 롤백 (필요시)
-- ALTER TABLE users
-- DROP COLUMN new_column;
```

## 실행 방법

### 방법 1: psql 사용
```bash
psql $DATABASE_URL -f migrations/20260116_add_refresh_token_to_users.sql
```

### 방법 2: Supabase Dashboard
1. Supabase Dashboard 접속
2. SQL Editor 메뉴 선택
3. 마이그레이션 SQL 파일 내용 복사-붙여넣기
4. Run 버튼 클릭

## 주의사항

- ⚠️ **프로덕션 적용 전 테스트 필수**
- ⚠️ **롤백 쿼리 확인 후 실행**
- ⚠️ **schema.sql도 함께 업데이트**
