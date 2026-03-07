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

CREATE TABLE IF NOT EXISTS customer_lifetime_value_per_segment (
    segment VARCHAR,
    average_clv DECIMAL(10, 2),
    total_customers INTEGER,
    total_revenue DECIMAL(10, 2)
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

-- Calculate Customer Lifetime Value (CLV) per Segment
INSERT INTO customer_lifetime_value_per_segment
WITH customer_total_spend AS (
    SELECT
        c.customer_id,
        c.segment,
        SUM(o.quantity * p.price) AS total_spend
    FROM read_csv_auto('{{ RAW_DIR }}/customers.csv') c
    LEFT JOIN read_csv_auto('{{ RAW_DIR }}/orders.csv') o ON c.customer_id = o.customer_id
    LEFT JOIN read_csv_auto('{{ RAW_DIR }}/products.csv') p ON o.product_id = p.product_id
    GROUP BY c.customer_id, c.segment
)
SELECT
    segment,
    ROUND(AVG(COALESCE(total_spend, 0)), 2) AS average_clv,
    COUNT(customer_id) AS total_customers,
    ROUND(SUM(COALESCE(total_spend, 0)), 2) AS total_revenue
FROM customer_total_spend
GROUP BY segment
ORDER BY average_clv DESC;
