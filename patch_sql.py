import sys

with open('SQL/Insert_Transaction.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

oldSql = """    -- 5. Insert Child Arrays (Options)
    INSERT IGNORE INTO Options (vehicle_id, option_code)
    SELECT 
        v.vehicle_id,
        opt.option_value
    FROM staging_allGM s
    CROSS JOIN JSON_TABLE(
        JSON_EXTRACT(s.allJson, '$.Options'),
        '$[*]' COLUMNS(option_value VARCHAR(50) PATH '$')
    ) AS opt
    JOIN Vehicles v ON v.vin = s.vin
    LEFT JOIN Options o ON o.vehicle_id = v.vehicle_id AND o.option_code = opt.option_value
    WHERE o.option_id IS NULL;"""

newSql = """    -- 5. Insert Child Arrays (Options)
    INSERT IGNORE INTO Options (vehicle_id, option_code)
    SELECT 
        v.vehicle_id,
        opt.option_value
    FROM staging_allGM s
    CROSS JOIN JSON_TABLE(
        JSON_EXTRACT(s.allJson, '$.Options'),
        '$[*]' COLUMNS(option_value VARCHAR(50) PATH '$')
    ) AS opt
    JOIN Vehicles v ON v.vin = s.vin;"""

if "o.option_id IS NULL" in sql:
    sql = sql.replace(oldSql, newSql)
    with open('SQL/Insert_Transaction.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    print("Success")
else:
    print("Not found")
