-- Transform logic to clean data and calculate business metrics

-- Create final tables to store the results
CREATE TABLE IF NOT EXISTS daily_revenue (
    order_date DATE,
    total_revenue DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS top_products_per_day (
    order_date DATE,
    product_id INTEGER,
    product_name VARCHAR,
    total_sales DECIMAL(10, 2),
    rank INTEGER
);

-- Calculate daily total revenue
INSERT INTO daily_revenue
SELECT
    CAST(o.order_date AS DATE) AS order_date,
    SUM(o.quantity * p.price) AS total_revenue
FROM read_csv_auto('{{ RAW_DIR }}/orders.csv') o
JOIN read_csv_auto('{{ RAW_DIR }}/products.csv') p ON o.product_id = p.product_id
GROUP BY CAST(o.order_date AS DATE)
ORDER BY order_date DESC;

-- Calculate top 5 selling products per day
INSERT INTO top_products_per_day
WITH daily_product_sales AS (
    SELECT
        CAST(o.order_date AS DATE) AS order_date,
        p.product_id,
        p.product_name,
        SUM(o.quantity * p.price) AS total_sales
    FROM read_csv_auto('{{ RAW_DIR }}/orders.csv') o
    JOIN read_csv_auto('{{ RAW_DIR }}/products.csv') p ON o.product_id = p.product_id
    GROUP BY CAST(o.order_date AS DATE), p.product_id, p.product_name
),
ranked_sales AS (
    SELECT *,
           ROW_NUMBER() OVER(PARTITION BY order_date ORDER BY total_sales DESC) as rank
    FROM daily_product_sales
)
SELECT order_date, product_id, product_name, total_sales, rank
FROM ranked_sales
WHERE rank <= 5
ORDER BY order_date DESC, rank ASC;
