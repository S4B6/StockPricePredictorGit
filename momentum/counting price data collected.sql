-- Main query to count data points, detect duplicates in date-ticker pairs, and add last fetch date

WITH data_points_count AS (
    SELECT 
        t.asset_class AS asset_class,
        t.ticker AS ticker,
        t.name AS name,
        COUNT(dp.id) AS data_points,
        MAX(dp.fetch_date) AS last_fetch_date  -- Get the latest fetch date for each ticker
    FROM 
        markets_equity_tickers t
    LEFT JOIN 
        markets_dailyprice dp 
    ON 
        t.ticker = dp.ticker
    WHERE 
        t.ticker IS NOT NULL AND t.ticker <> ''  -- Exclude empty or null tickers
    GROUP BY 
        t.asset_class, t.ticker, t.name

    UNION ALL

    SELECT 
        t.asset_class AS asset_class,
        t.ticker AS ticker,
        t.name AS name,
        COUNT(dp.id) AS data_points,
        MAX(dp.fetch_date) AS last_fetch_date
    FROM 
        markets_bond_tickers t
    LEFT JOIN 
        markets_dailyprice dp 
    ON 
        t.ticker = dp.ticker
    WHERE 
        t.ticker IS NOT NULL AND t.ticker <> ''  -- Exclude empty or null tickers
    GROUP BY 
        t.asset_class, t.ticker, t.name

    UNION ALL

    SELECT 
        t.asset_class AS asset_class,
        t.ticker AS ticker,
        t.name AS name,
        COUNT(dp.id) AS data_points,
        MAX(dp.fetch_date) AS last_fetch_date
    FROM 
        markets_forex_tickers t
    LEFT JOIN 
        markets_dailyprice dp 
    ON 
        t.ticker = dp.ticker
    WHERE 
        t.ticker IS NOT NULL AND t.ticker <> ''  -- Exclude empty or null tickers
    GROUP BY 
        t.asset_class, t.ticker, t.name

    UNION ALL

    SELECT 
        t.asset_class AS asset_class,
        t.ticker AS ticker,
        t.name AS name,
        COUNT(dp.id) AS data_points,
        MAX(dp.fetch_date) AS last_fetch_date
    FROM 
        markets_cryptocurrency_tickers t
    LEFT JOIN 
        markets_dailyprice dp 
    ON 
        t.ticker = dp.ticker
    WHERE 
        t.ticker IS NOT NULL AND t.ticker <> ''  -- Exclude empty or null tickers
    GROUP BY 
        t.asset_class, t.ticker, t.name

    UNION ALL

    SELECT 
        t.asset_class AS asset_class,
        t.ticker AS ticker,
        t.name AS name,
        COUNT(dp.id) AS data_points,
        MAX(dp.fetch_date) AS last_fetch_date
    FROM 
        markets_commodity_tickers t
    LEFT JOIN 
        markets_dailyprice dp 
    ON 
        t.ticker = dp.ticker
    WHERE 
        t.ticker IS NOT NULL AND t.ticker <> ''  -- Exclude empty or null tickers
    GROUP BY 
        t.asset_class, t.ticker, t.name
),

-- Total count without a last fetch date
total_data_points AS (
    SELECT 
        'Total' AS asset_class,
        NULL AS ticker,
        NULL AS name,
        SUM(data_points) AS data_points,
        NULL::timestamp with time zone AS last_fetch_date  -- Cast NULL to timestamp with time zone
    FROM data_points_count
),

-- Duplicate check for date-ticker pairs without a last fetch date
duplicate_check AS (
    SELECT 
        'Duplicates' AS asset_class,
        NULL AS ticker,
        NULL AS name,
        COUNT(*) AS data_points,
        NULL::timestamp with time zone AS last_fetch_date  -- Cast NULL to timestamp with time zone
    FROM (
        SELECT 
            date,
            ticker,
            COUNT(*) AS duplicate_count
        FROM markets_dailyprice
        GROUP BY date, ticker
        HAVING COUNT(*) > 1  -- Identifies duplicates
    ) AS duplicates
)

-- Combine all results
SELECT * FROM data_points_count
UNION ALL
SELECT * FROM total_data_points
UNION ALL
SELECT * FROM duplicate_check
ORDER BY data_points ASC;
