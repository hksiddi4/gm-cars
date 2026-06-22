DROP PROCEDURE IF EXISTS execute_gm_data_sync;

CALL execute_gm_data_sync();

DELIMITER //

CREATE PROCEDURE execute_gm_data_sync()
BEGIN
    -- Automatically rollback the transaction if any SQL error occurs
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ETL Pipeline failed; transaction rolled back.';
    END;

    START TRANSACTION;

    -- 1. Insert Base Lookup Data
    INSERT INTO Engines (engine_type)
    SELECT DISTINCT s.vehicleEngine
    FROM staging_allGM s
    LEFT JOIN Engines e ON e.engine_type = s.vehicleEngine
    WHERE s.vehicleEngine IS NOT NULL AND e.engine_id IS NULL;

    INSERT INTO Transmissions (transmission_type)
    SELECT DISTINCT s.transmission
    FROM staging_allGM s
    LEFT JOIN Transmissions t ON t.transmission_type = s.transmission
    WHERE s.transmission IS NOT NULL AND t.transmission_id IS NULL;

    INSERT INTO Drivetrains (drivetrain_type)
    SELECT DISTINCT s.drivetrain
    FROM staging_allGM s
    LEFT JOIN Drivetrains d ON d.drivetrain_type = s.drivetrain
    WHERE s.drivetrain IS NOT NULL AND d.drivetrain_id IS NULL;

    INSERT INTO Colors (color_name)
    SELECT DISTINCT s.exterior_color
    FROM staging_allGM s
    LEFT JOIN Colors c ON c.color_name = s.exterior_color
    WHERE s.exterior_color IS NOT NULL AND c.color_id IS NULL;

    -- 2. Insert Complex Lookups
    INSERT IGNORE INTO Dealers (dealer_name, location, sitedealer_code)
    SELECT DISTINCT 
        s.dealer, 
        s.location, 
        JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sitedealer_code')) AS sitedealer_code
    FROM staging_allGM s
    WHERE s.dealer IS NOT NULL;

    INSERT IGNORE INTO MMC_Codes (mmc_code)
    SELECT DISTINCT REPLACE(JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.mmc_code')), ' ', '') AS cleaned_mmc
    FROM staging_allGM s
    LEFT JOIN MMC_Codes m ON m.mmc_code = REPLACE(JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.mmc_code')), ' ', '')
    WHERE JSON_EXTRACT(s.allJson, '$.mmc_code') IS NOT NULL AND m.mmc_code_id IS NULL;

    -- 3. Insert Orders
    INSERT IGNORE INTO Orders (order_number, creation_date, mmc_code_id, sell_source, country)
    SELECT 
        s.ordernum, 
        CASE
            WHEN JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.creation_date')) = 'N/A' THEN NULL
            ELSE STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.creation_date')), '%m/%d/%Y')
        END AS creation_date,
        m.mmc_code_id,
        JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sell_source')) AS sell_source,
        CASE
            WHEN JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sell_source')) = 'N/A' THEN 'MEXICO'
            WHEN JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sell_source')) = '14' THEN 'CANADA'
            ELSE 'USA'
        END AS country
    FROM staging_allGM s
    LEFT JOIN MMC_Codes m ON m.mmc_code = REPLACE(JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.mmc_code')), ' ', '')
    LEFT JOIN Orders o ON o.order_number = s.ordernum
    WHERE s.ordernum IS NOT NULL AND s.ordernum != '' AND o.order_id IS NULL;

    -- 4. Insert Main Core Data (Vehicles)
    INSERT IGNORE INTO Vehicles (vin, modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, dealer_id, order_id)
    SELECT 
        s.vin, 
        s.modelYear, 
        s.model, 
        s.body, 
        s.trim,
        e.engine_id,
        t.transmission_id,
        d.drivetrain_id,
        c.color_id,
        s.msrp,
        dl.dealer_id,
        o.order_id
    FROM staging_allGM s
    LEFT JOIN Engines e ON e.engine_type = s.vehicleEngine
    LEFT JOIN Transmissions t ON t.transmission_type = s.transmission
    LEFT JOIN Drivetrains d ON d.drivetrain_type = s.drivetrain
    LEFT JOIN Colors c ON c.color_name = s.exterior_color
    LEFT JOIN Dealers dl ON dl.dealer_name = s.dealer 
                        AND dl.location = s.location 
                        AND dl.sitedealer_code = JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sitedealer_code'))
    LEFT JOIN Orders o ON o.order_number = s.ordernum
    LEFT JOIN Vehicles v ON v.vin = s.vin
    WHERE v.vehicle_id IS NULL;

    -- 5. Insert Child Arrays (Options)
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
    WHERE o.option_id IS NULL;

    -- 6. Insert Edge Features (SpecialEditions) - SCOPED TO STAGING
    INSERT IGNORE INTO SpecialEditions (vehicle_id, special_desc)
    SELECT v.vehicle_id, special_map.special_desc
    FROM staging_allGM s
    JOIN Vehicles v ON v.vin = s.vin
    JOIN Options opt ON v.vehicle_id = opt.vehicle_id
    CROSS JOIN (
		SELECT 'A1X' AS rpo_code, '1LE' AS special_desc
		UNION ALL SELECT 'A1Y', '1LE'
		UNION ALL SELECT 'Z4B', 'Collectors Edition'
		UNION ALL SELECT 'X56', 'Garage 56 Special Edition'
		UNION ALL SELECT 'Z51', 'Z51 Performance Package'
		UNION ALL SELECT 'ZCR', 'IMSA GTLM Championship C8.R Edition'
		UNION ALL SELECT 'Y70', '70th Anniversary Edition'
		UNION ALL SELECT 'Z07', 'Z07 Performance Package'
		UNION ALL SELECT 'ZLE', 'Watkins Glen IMSA Edition'
		UNION ALL SELECT 'ZLD', 'Sebring IMSA Edition'
		UNION ALL SELECT 'ZLG', 'Road Atlanta IMSA Edition'
		UNION ALL SELECT 'ZLK', 'Arrival Edition'
		UNION ALL SELECT 'ZLJ', 'Impact Edition'
		UNION ALL SELECT 'ZLR', 'Elevation Edition'
		UNION ALL SELECT 'ABQ', '120th Anniversary Edition'
		UNION ALL SELECT 'OAR', 'Pre-Production Vehicle'
		UNION ALL SELECT 'PEH', 'Hertz / Hendrick Motorsports Edition'
		UNION ALL SELECT 'ZLT', '20th Anniversary of V-Series Special Edition'
		UNION ALL SELECT 'ZLV', '20th Anniversary of V-Series Special Edition'
		UNION ALL SELECT 'ZTK', 'ZTK Track Performance Package'
		UNION ALL SELECT 'Z6X', 'Extreme Off-Road Package'
		UNION ALL SELECT 'WFP', 'Omega Edition'
		UNION ALL SELECT 'ZRA', 'Quail Silver Limited Edition'
		UNION ALL SELECT 'USA', 'Stars & Steel Limited Edition'
		UNION ALL SELECT 'V8V', 'Precision Package'
		UNION ALL SELECT 'PCK', 'Deep Ocean Appearance Package'
		UNION ALL SELECT 'Z25', 'Grand Sport Launch Edition'
		UNION ALL SELECT 'FEB', 'Z52 Sport Performance Package'
		UNION ALL SELECT 'FEY', 'Z52 Track Performance Package'
    ) AS special_map ON opt.option_code = special_map.rpo_code
    LEFT JOIN SpecialEditions se ON se.vehicle_id = v.vehicle_id AND se.special_desc = special_map.special_desc
    WHERE se.special_id IS NULL
    AND (special_map.rpo_code != 'PCK' OR v.model = 'CT5');

    COMMIT;
END //

DELIMITER ;