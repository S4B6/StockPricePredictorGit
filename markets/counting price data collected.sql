SELECT 
    t.asset_class AS asset_class,
    t.ticker AS ticker,
    t.name AS name,
    COUNT(dp.id) AS data_points
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
    COUNT(dp.id) AS data_points
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
    COUNT(dp.id) AS data_points
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
    COUNT(dp.id) AS data_points
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
    COUNT(dp.id) AS data_points
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

ORDER BY 
    data_points ASC;
