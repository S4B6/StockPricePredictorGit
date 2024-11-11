DO $$
DECLARE
    table_name TEXT;
BEGIN
    -- Loop through all tables starting with 'markets_'
    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename LIKE 'markets_%'
    LOOP
        -- Drop each table with CASCADE
        EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE;', table_name);
    END LOOP;
END $$;

DELETE FROM django_migrations WHERE app = 'markets';