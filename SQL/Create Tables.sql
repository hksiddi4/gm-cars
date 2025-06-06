create database vehicles;
use vehicles;
create user 'hussain' identified by 'Hussain92';
grant all privileges on vehicles.* to 'hussain'@'%';
drop database vehicles;

start transaction;
-- staging_allGM
CREATE TABLE IF NOT EXISTS staging_allGM (
	vin varchar(17) PRIMARY KEY,
    modelYear int,
    model varchar(75),
    body varchar(20),
    trim varchar(25),
    vehicleEngine varchar(75),
    transmission varchar(7),
    drivetrain varchar(3),
    exterior_color varchar(75),
    msrp int,
    dealer varchar(75),
    location varchar(75),
    ordernum varchar(6),
    allJson json
);

-- Engines Table
CREATE TABLE Engines (
    engine_id SERIAL PRIMARY KEY,
    engine_type VARCHAR(48) UNIQUE
);

-- Transmissions Table
CREATE TABLE Transmissions (
    transmission_id SERIAL PRIMARY KEY,
    transmission_type VARCHAR(4) UNIQUE
);

-- Drivetrains Table
CREATE TABLE Drivetrains (
    drivetrain_id SERIAL PRIMARY KEY,
    drivetrain_type VARCHAR(3) UNIQUE
);

-- Colors Table
CREATE TABLE Colors (
    color_id SERIAL PRIMARY KEY,
    color_name VARCHAR(32) UNIQUE,
    rpo_code VARCHAR(3)
);

-- Dealers Table with sitedealer_code
CREATE TABLE Dealers (
    dealer_id SERIAL PRIMARY KEY,
    dealer_name VARCHAR(64),
    location VARCHAR(64),
    sitedealer_code VARCHAR(5)
);

-- MMC Codes Table
CREATE TABLE MMC_Codes (
    mmc_code_id SERIAL PRIMARY KEY,
    mmc_code VARCHAR(5) UNIQUE
);

-- Orders Table
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(6) UNIQUE,
    creation_date DATE,
    mmc_code_id INTEGER REFERENCES MMC_Codes(mmc_code_id),
    sell_source VARCHAR(2),
    country VARCHAR(8)
);

-- Vehicles Table
CREATE TABLE Vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,
    modelYear INTEGER,
    model VARCHAR(32),
    body VARCHAR(16),
    trim VARCHAR(32),
    engine_id INTEGER REFERENCES Engines(engine_id),
    transmission_id INTEGER REFERENCES Transmissions(transmission_id),
    drivetrain_id INTEGER REFERENCES Drivetrains(drivetrain_id),
    color_id INTEGER REFERENCES Colors(color_id),
    msrp INTEGER,
    dealer_id INTEGER REFERENCES Dealers(dealer_id),
    order_id INTEGER REFERENCES Orders(order_id)
);

-- Options Table
CREATE TABLE Options (
    option_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES Vehicles(vehicle_id),
    option_code CHAR(3),
    UNIQUE (vehicle_id, option_code)
);

-- Special Editions Table
CREATE TABLE SpecialEditions (
	special_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES Vehicles(vehicle_id),
    special_desc VARCHAR(64)
);

COMMIT;

-- Indexes for faster querying
-- Composite Index for Frequent Filtering and Grouping
CREATE INDEX idx_vehicle_model_info ON Vehicles(modelYear, model, body, trim);
-- Sorting and Filtering on modelYear, engine_id, and msrp
CREATE INDEX idx_vehicle_filter_sort ON Vehicles(modelYear, engine_id, msrp, model);
-- Orders Table (index on creation_date for faster date-based queries)
CREATE INDEX idx_order_creation_date ON Orders(creation_date);
-- Options Table (composite index for vehicle_id and option_code)
CREATE INDEX idx_options_vehicle_code ON Options(vehicle_id, option_code);
-- Index for SpecialEditions table (left join optimization and GROUP_CONCAT)
CREATE INDEX idx_special_edition_vehicle ON SpecialEditions(vehicle_id, special_desc);
-- Foreign Key Indexes for Faster Joins in the Vehicles table
CREATE INDEX idx_vehicle_color_id ON Vehicles(color_id);
CREATE INDEX idx_vehicle_order_id ON Vehicles(order_id);

CREATE INDEX idx_vehicle_composite ON Vehicles(modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, order_id);

-- Test with EXPLAIN for any perf gains
-- Model Year
CREATE INDEX idx_vehicle_modelYear ON Vehicles(modelYear);
CREATE INDEX idx_engine_lookup ON Engines(engine_id, engine_type);
CREATE INDEX idx_transmission_lookup ON Transmissions(transmission_id, transmission_type);
CREATE INDEX idx_drivetrain_lookup ON Drivetrains(drivetrain_id, drivetrain_type);

-- Insert Engine Types
INSERT INTO Engines (engine_type)
SELECT DISTINCT vehicleEngine
FROM staging_allGM
WHERE vehicleEngine NOT IN (SELECT engine_type FROM Engines);
SELECT * FROM Engines;

-- Insert Transmission Types
INSERT INTO Transmissions (transmission_type)
SELECT DISTINCT Transmission FROM staging_allGM
WHERE Transmission NOT IN (SELECT transmission_type FROM Transmissions);
SELECT * FROM Transmissions;

-- Insert Drivetrain Types
INSERT INTO Drivetrains (drivetrain_type)
SELECT DISTINCT Drivetrain FROM staging_allGM
WHERE drivetrain NOT IN (SELECT drivetrain_type FROM Drivetrains);
SELECT * FROM Drivetrains;

-- Insert Colors
INSERT INTO Colors (color_name)
SELECT DISTINCT exterior_color FROM staging_allGM
WHERE exterior_color NOT IN (SELECT color_name FROM Colors);
SELECT * FROM Colors;

-- Insert Dealers
INSERT INTO Dealers (dealer_name, location, sitedealer_code)
SELECT DISTINCT 
    dealer, 
    location, 
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) AS sitedealer_code
FROM staging_allGM
WHERE (dealer, location, JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code'))) 
      NOT IN (SELECT dealer_name, location, sitedealer_code FROM Dealers);
SELECT * FROM Dealers ORDER BY SITEDEALER_CODE;

-- Check Duplicate Dealers
SELECT
    sitedealer_code,
    COUNT(*) AS occurrences
FROM Dealers GROUP BY sitedealer_code HAVING occurrences > 1;
SELECT * FROM Dealers WHERE sitedealer_code = '16173';

SELECT v.* 
FROM Vehicles v
JOIN Dealers d ON v.dealer_id = d.dealer_id
WHERE d.sitedealer_code = '16173';

-- Insert MMC Codes
INSERT IGNORE INTO MMC_Codes (mmc_code)
SELECT DISTINCT REPLACE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')), ' ', '') AS mmc_code 
FROM staging_allGM
WHERE REPLACE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')), ' ', '') NOT IN (SELECT mmc_code FROM MMC_Codes);
SELECT * FROM MMC_Codes;

-- Insert Orders
INSERT IGNORE INTO Orders (order_number, creation_date, mmc_code_id, sell_source, country)
SELECT 
    ordernum, 
    CASE
        WHEN JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.creation_date')) = 'N/A' THEN NULL
        ELSE STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.creation_date')), '%m/%d/%Y')
    END AS creation_date,
    (SELECT mmc_code_id 
     FROM MMC_Codes 
     WHERE mmc_code = JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code'))) AS mmc_code_id,
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sell_source')) AS sell_source,
    CASE
        WHEN JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sell_source')) = 'N/A' THEN 'MEXICO'
        WHEN JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sell_source')) = '14' THEN 'CANADA'
        ELSE 'USA'
    END AS country
FROM staging_allGM
WHERE ordernum IS NOT NULL AND ordernum != '' AND ordernum NOT IN (SELECT order_number FROM Orders);
SELECT * FROM Orders;
select * from staging_allGM where vin = '1G6D35R67R0912024';

-- Find/edit Order duplicates
	SELECT
		JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.order_number')) AS order_number,
		COUNT(*) AS occurrences
	FROM staging_allGM GROUP BY order_number HAVING occurrences > 1;

	SELECT COUNT(vin) FROM Vehicles;

	UPDATE staging_allGM
	SET
	TRIM = 'LUXURY',
	vehicleEngine = '2.0L TURBO, 4-CYL, SIDI',
	DRIVETRAIN = 'RWD',
	exterior_color = 'BLACK RAVEN',
	MSRP = '41710',
	DEALER = 'CENTRAL CADILLAC',
	LOCATION = 'JONESBORO, AR 72403-6600',
	ORDERNUM = 'XXKDJ3',
	allJson = '{"maker":"CADILLAC", "model_year":"2021", "mmc_code":"6DB79", "vin":"1G6DW5RK1M0108427", "sitedealer_code":"17270", "sell_source": "12", "order_number": "XXKDJ3", "creation_date":"10/9/2020", "Options":["AEF", "AER", "AHP", "AJC", "AJW", "AKP", "AL0", "AL9", "AM9", "AQ9", "ATH", "AT8", "AT9", "AVN", "AXG", "AXJ", "AYG", "A2X", "A7J", "BTV", "BYO", "B34", "B35", "B56", "CE1", "CJ2", "C3U", "DEG", "DWK", "D31", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "GBA", "HRD", "HS1", "H2G", "IOT", "JJ2", "JL9", "JM8", "J21", "J77", "KA1", "KBC", "KD4", "KI3", "KL9", "KPA", "KRV", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDE", "MHS", "NB9", "NE8", "NP5", "NTB", "N37", "PCM", "PPW", "QBC", "Q81", "RWL", "RYT", "R6R", "R7E", "R8R", "R9N", "SLM", "S08", "TDM", "TFK", "TTW", "T4L", "T8Z", "UDD", "UEU", "UE1", "UGC", "UGE", "UG1", "UHY", "UIT", "UJN", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VK3", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WMU", "XL8", "YM8", "Y19", "Y26", "Y5V", "0ST", "1NF", "1SB", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "719", "8X2", "9L3", "9X2"]}'
	WHERE vin = '1G6DW5RK1M0108427';
	SELECT * FROM staging_allGM WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.order_number')) = 'ZDMJR6';

-- Insert Vehicles
INSERT IGNORE INTO Vehicles (vin, modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, dealer_id, order_id)
SELECT vin, modelYear, model, body, trim,
    (SELECT engine_id FROM Engines WHERE engine_type = vehicleEngine) AS engine_id,
    (SELECT transmission_id FROM Transmissions WHERE transmission_type = transmission) AS transmission_id,
    (SELECT drivetrain_id FROM Drivetrains WHERE drivetrain_type = drivetrain) AS drivetrain_id,
    (SELECT color_id FROM Colors WHERE color_name = exterior_color) AS color_id,
    msrp,
    (SELECT dealer_id FROM Dealers WHERE dealer_name = dealer AND location = location AND sitedealer_code = JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) LIMIT 1) AS dealer_id,
    (SELECT order_id FROM Orders WHERE order_number = ordernum) AS order_id
FROM staging_allGM
WHERE vin NOT IN (SELECT vin FROM Vehicles);

select * from Vehicles where vin = '1G1F91R68R0100043';
SELECT v.vin, v.modelYear, v.model, v.body, v.trim,
            e.engine_type, t.transmission_type, d.drivetrain_type,
            c.color_name, v.msrp, o.country,
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
        FROM Vehicles v
            JOIN Engines e ON v.engine_id = e.engine_id
            JOIN Transmissions t ON v.transmission_id = t.transmission_id
            JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
            JOIN Colors c ON v.color_id = c.color_id
            JOIN Orders o ON v.order_id = o.order_id
            LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        where vin = '1G1F91R68R0100043'
        GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim,
                e.engine_type, t.transmission_type, d.drivetrain_type,
                c.color_name, v.msrp, o.country;

-- Fix Mexico VIN Orders to Display with all vehicles
INSERT INTO Orders (order_number, mmc_code_id, country)
VALUES ('XXXXXX', 1, 'MEXICO');
select * from Orders where order_number = 'XXXXXX';
UPDATE Vehicles SET order_id = '393211' WHERE vehicle_id = 20; -- Set for all 20 Mexico ZL1 Collector's Editions

-- Test efficient Insert Vehicles
CREATE TEMPORARY TABLE staging_resolved AS
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
    de.dealer_id,
    o.order_id
FROM staging_allGM s
LEFT JOIN Engines e ON s.vehicleEngine = e.engine_type
LEFT JOIN Transmissions t ON s.transmission = t.transmission_type
LEFT JOIN Drivetrains d ON s.drivetrain = d.drivetrain_type
LEFT JOIN Colors c ON s.exterior_color = c.color_name
LEFT JOIN Dealers de ON TRIM(LOWER(s.dealer)) = TRIM(LOWER(de.dealer_name))
                     AND TRIM(LOWER(s.location)) = TRIM(LOWER(de.location))
                     AND JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.sitedealer_code')) = de.sitedealer_code
LEFT JOIN Orders o ON s.ordernum = o.order_number;

INSERT IGNORE INTO Vehicles (
    vin, modelYear, model, body, trim,
    engine_id, transmission_id, drivetrain_id,
    color_id, msrp, dealer_id, order_id
)
SELECT
    vin, modelYear, model, body, trim,
    engine_id, transmission_id, drivetrain_id,
    color_id, msrp, dealer_id, order_id
FROM staging_resolved
WHERE vin NOT IN (SELECT vin FROM Vehicles);

DROP TEMPORARY TABLE IF EXISTS staging_resolved;

-- Insert Options with error handling
SET GLOBAL innodb_buffer_pool_size = 10 * 1024 * 1024 * 1024;  -- 10GB in bytes
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
WHERE (v.vehicle_id, opt.option_value) NOT IN (SELECT vehicle_id, option_code FROM Options);
select * from options where vehicle_id = 1;

INSERT IGNORE INTO SpecialEditions (vehicle_id, special_desc)
SELECT vehicle_id, special_desc
FROM (
    SELECT v.vehicle_id, 
           JSON_UNQUOTE(JSON_EXTRACT(s.allJson, '$.Options')) AS options
    FROM staging_allGM s
    JOIN Vehicles v ON s.vin = v.vin
) rpo_match
CROSS JOIN LATERAL (
    SELECT '1LE' AS special_desc WHERE options LIKE '%"A1X"%' OR options LIKE '%"A1Y"%' OR options LIKE '%"A1Z"%'
    UNION ALL
    SELECT 'Collectors Edition' WHERE options LIKE '%"Z4B"%'
    UNION ALL
    SELECT 'Garage 56 Special Edition' WHERE options LIKE '%"X56"%'
    UNION ALL
    SELECT 'Z51 Performance Package' WHERE options LIKE '%"Z51"%'
    UNION ALL
    SELECT 'IMSA GTLM Championship C8.R Edition' WHERE options LIKE '%"ZCR"%'
    UNION ALL
    SELECT '70th Anniversary Edition' WHERE options LIKE '%"Y70"%'
    UNION ALL
    SELECT 'Z07 Performance Package' WHERE options LIKE '%"Z07"%'
    UNION ALL
    SELECT 'Watkins Glen IMSA Edition' WHERE options LIKE '%"ZLE"%'
    UNION ALL
    SELECT 'Sebring IMSA Edition' WHERE options LIKE '%"ZLD"%'
    UNION ALL
    SELECT 'Road Atlanta IMSA Edition' WHERE options LIKE '%"ZLG"%'
    UNION ALL
    SELECT 'Arrival Edition' WHERE options LIKE '%"ZLK"%'
    UNION ALL
    SELECT 'Impact Edition' WHERE options LIKE '%"ZLJ"%'
    UNION ALL
    SELECT 'Elevation Edition' WHERE options LIKE '%"ZLR"%'
    UNION ALL
    SELECT '120th Anniversary Edition' WHERE options LIKE '%"ABQ"%'
    UNION ALL
    SELECT 'Pre-Production Vehicle' WHERE options LIKE '%"OAR"%'
    UNION ALL
    SELECT 'Hertz / Hendrick Motorsports Edition' WHERE options LIKE '%"PEH"%'
    UNION ALL
    SELECT '20th Anniversary of V-Series Special Edition' WHERE options LIKE '%"ZLT"%'
) special_editions
WHERE special_desc IS NOT NULL
AND NOT EXISTS (
    SELECT 1 
    FROM SpecialEditions se 
    WHERE se.vehicle_id = rpo_match.vehicle_id 
    AND se.special_desc = special_editions.special_desc
);
select * from SpecialEditions;

SELECT se.special_desc, v.vin
FROM SpecialEditions se
JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
WHERE v.color_id = 1
  AND se.special_desc LIKE '%Collectors Edition%'
ORDER BY SUBSTRING(v.vin, -6);

start transaction;
WITH OrderedEditions AS (
    SELECT se.vehicle_id, ROW_NUMBER() OVER (ORDER BY SUBSTRING(v.vin, -6)) AS row_num
    FROM SpecialEditions se
    JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
    WHERE v.color_id = 1
      AND se.special_desc LIKE '%Collectors Edition%'
)
UPDATE SpecialEditions se
JOIN OrderedEditions oe ON se.vehicle_id = oe.vehicle_id
SET se.special_desc = CONCAT('Collectors Edition #', LPAD(oe.row_num, 3, '0'));

WITH OrderedEditions AS (
    SELECT se.vehicle_id, ROW_NUMBER() OVER (ORDER BY SUBSTRING(v.vin, -6)) AS row_num
    FROM SpecialEditions se
    JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
    WHERE v.color_id = 16
      AND se.special_desc LIKE '%Garage 56 Special Edition%'
)
UPDATE SpecialEditions se
JOIN OrderedEditions oe ON se.vehicle_id = oe.vehicle_id
SET se.special_desc = CONCAT('Garage 56 Special Edition #', LPAD(oe.row_num, 2, '0'));
commit;

WITH OrderedEditions AS (
    SELECT se.vehicle_id, ROW_NUMBER() OVER (ORDER BY SUBSTRING(v.vin, -6)) AS row_num
    FROM SpecialEditions se
    JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
    WHERE v.color_id = 1
      AND se.special_desc LIKE '%Collectors Edition%'
)
SELECT se.vehicle_id, se.special_desc, CONCAT('Collectors Edition #', LPAD(oe.row_num, 3, '0')) AS new_special_desc
FROM SpecialEditions se
JOIN OrderedEditions oe ON se.vehicle_id = oe.vehicle_id
WHERE se.special_desc LIKE '%Collectors Edition%'
ORDER BY oe.row_num;

select * from Vehicles where vin = '1G6D25R65R0962018';

SELECT se.special_desc, v.vin
FROM SpecialEditions se
JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
WHERE v.vin = '1G6D25R65R0962018';

UPDATE SpecialEditions se
JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
SET se.special_desc = 'CT5-V Blackwing 20th Anniversary Edition'
WHERE v.vin = '1G6D25R65R0962018';

insert into SpecialEditions (vehicle_id, special_desc) values (286143, 'CT5-V Blackwing 20th Anniversary Edition');

WITH ColorCounts AS (
    SELECT
        crm.rpo_code,
        COUNT(*) AS total_count,
        GROUP_CONCAT(DISTINCT crm.color_name ORDER BY crm.color_name SEPARATOR ', ') AS color_names
    FROM Vehicles v
    JOIN Colors c ON v.color_id = c.color_id
    JOIN ColorRPOMap crm ON c.color_name = crm.color_name
    GROUP BY crm.rpo_code
),
Ranked AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY total_count DESC) AS `rank`,
        rpo_code,
        total_count,
        color_names,
        ROUND(100.0 * total_count / SUM(total_count) OVER (), 2) AS percent
    FROM ColorCounts
)
SELECT * FROM Ranked;

UPDATE Colors SET rpo_code = 'G4Z' WHERE color_name = 'ROSWELL GREEN METALLIC';
UPDATE Colors SET rpo_code = 'GD0' WHERE color_name = 'ACCELERATE YELLOW METALLIC';
UPDATE Colors SET rpo_code = 'GC5' WHERE color_name = 'AMPLIFY ORANGE TINTCOAT';
UPDATE Colors SET rpo_code = 'G8G' WHERE color_name = 'ARCTIC WHITE';
UPDATE Colors SET rpo_code = 'GXD' WHERE color_name = 'ARGENT SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GLK' WHERE color_name = 'BLACK DIAMOND TRICOAT';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'BLACK RAVEN';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'BLACK';
UPDATE Colors SET rpo_code = 'GAN' WHERE color_name = 'BLADE SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GCF' WHERE color_name = 'BLAZE METALLIC';
UPDATE Colors SET rpo_code = 'GVR' WHERE color_name = 'CACTI GREEN';
UPDATE Colors SET rpo_code = 'G48' WHERE color_name = 'CAFFEINE METALLIC';
UPDATE Colors SET rpo_code = 'GAR' WHERE color_name = 'CARBON FLASH METALLIC';
UPDATE Colors SET rpo_code = 'G9F' WHERE color_name = 'CERAMIC MATRIX GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GJV' WHERE color_name = 'COASTAL BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GBK' WHERE color_name = 'COMPETITION YELLOW TINTCOAT METALLIC';
UPDATE Colors SET rpo_code = 'G16' WHERE color_name = 'CRUSH';
UPDATE Colors SET rpo_code = 'G1W' WHERE color_name = 'CRYSTAL WHITE TRICOAT';
UPDATE Colors SET rpo_code = 'GCP' WHERE color_name = 'CYBER YELLOW METALLIC';
UPDATE Colors SET rpo_code = 'G7W' WHERE color_name = 'DARK EMERALD FROST';
UPDATE Colors SET rpo_code = 'GLU' WHERE color_name = 'DARK MOON METALLIC';
UPDATE Colors SET rpo_code = 'GAI' WHERE color_name = 'DEEP SPACE METALLIC';
UPDATE Colors SET rpo_code = 'GMO' WHERE color_name = 'ELECTRIC BLUE';
UPDATE Colors SET rpo_code = 'GS7' WHERE color_name = 'ELKHART LAKE BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GJ0' WHERE color_name = 'EVERGREEN METALLIC';
UPDATE Colors SET rpo_code = 'GLR' WHERE color_name = 'GARNET METALLIC';
UPDATE Colors SET rpo_code = 'G7E' WHERE color_name = 'GARNET RED TINTCOAT';
UPDATE Colors SET rpo_code = 'GA7' WHERE color_name = 'HYPERSONIC GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GXL' WHERE color_name = 'HYSTERIA PURPLE METALLIC';
UPDATE Colors SET rpo_code = 'GSK' WHERE color_name = 'INFRARED TINTCOAT';
UPDATE Colors SET rpo_code = 'G1E' WHERE color_name = 'LONG BEACH RED METALLIC';
UPDATE Colors SET rpo_code = 'GCI' WHERE color_name = 'MANHATTAN NOIR METALLIC';
UPDATE Colors SET rpo_code = 'GNW' WHERE color_name = 'MAVERICK NOIR FROST';
UPDATE Colors SET rpo_code = 'GKA' WHERE color_name = 'MERCURY SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GXF' WHERE color_name = 'MIDNIGHT SKY METALLIC';
UPDATE Colors SET rpo_code = 'GXU' WHERE color_name = 'MIDNIGHT STEEL METALLIC';
UPDATE Colors SET rpo_code = 'GCP' WHERE color_name = 'NITRO YELLOW METALLIC';
UPDATE Colors SET rpo_code = 'GNW' WHERE color_name = 'PANTHER BLACK MATTE';
UPDATE Colors SET rpo_code = 'GLK' WHERE color_name = 'PANTHER BLACK METALLIC';
UPDATE Colors SET rpo_code = 'GNT' WHERE color_name = 'RADIANT RED TINTCOAT';
UPDATE Colors SET rpo_code = 'GAN' WHERE color_name = 'RADIANT SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GJ0' WHERE color_name = 'RALLY GREEN METALLIC';
UPDATE Colors SET rpo_code = 'GMO' WHERE color_name = 'RAPID BLUE';
UPDATE Colors SET rpo_code = 'GPJ' WHERE color_name = 'RED HORIZON TINTCOAT';
UPDATE Colors SET rpo_code = 'G7C' WHERE color_name = 'RED HOT';
UPDATE Colors SET rpo_code = 'GPH' WHERE color_name = 'RED MIST METALLIC TINTCOAT';
UPDATE Colors SET rpo_code = 'G7E' WHERE color_name = 'RED OBSESSION TINTCOAT';
UPDATE Colors SET rpo_code = 'GRW' WHERE color_name = 'RIFT METALLIC';
UPDATE Colors SET rpo_code = 'GJV' WHERE color_name = 'RIPTIDE BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GKK' WHERE color_name = 'RIVERSIDE BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GLL' WHERE color_name = 'ROYAL SPICE METALLIC';
UPDATE Colors SET rpo_code = 'G9K' WHERE color_name = 'SATIN STEEL GRAY METALLIC';
UPDATE Colors SET rpo_code = 'G9K' WHERE color_name = 'SATIN STEEL METALLIC';
UPDATE Colors SET rpo_code = 'GXA' WHERE color_name = 'SEA WOLF GRAY TRICOAT';
UPDATE Colors SET rpo_code = 'G26' WHERE color_name = 'SEBRING ORANGE';
UPDATE Colors SET rpo_code = 'GJI' WHERE color_name = 'SHADOW GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GJI' WHERE color_name = 'SHADOW METALLIC';
UPDATE Colors SET rpo_code = 'GXD' WHERE color_name = 'SHARKSKIN METALLIC';
UPDATE Colors SET rpo_code = 'GKO' WHERE color_name = 'SHOCK';
UPDATE Colors SET rpo_code = 'GSJ' WHERE color_name = 'SILVER FLARE METALLIC';
UPDATE Colors SET rpo_code = 'GB8' WHERE color_name = 'STELLAR BLACK METALLIC';
UPDATE Colors SET rpo_code = 'GAZ' WHERE color_name = 'SUMMIT WHITE';
UPDATE Colors SET rpo_code = 'GKZ' WHERE color_name = 'TORCH RED';
UPDATE Colors SET rpo_code = 'GBW' WHERE color_name = 'TYPHOON METALLIC';
UPDATE Colors SET rpo_code = 'G7C' WHERE color_name = 'VELOCITY RED';
UPDATE Colors SET rpo_code = 'GCF' WHERE color_name = 'VIVID ORANGE METALLIC';
UPDATE Colors SET rpo_code = 'GKK' WHERE color_name = 'WAVE METALLIC';
UPDATE Colors SET rpo_code = 'G1W' WHERE color_name = 'WHITE PEARL METALLIC TRICOAT';
UPDATE Colors SET rpo_code = 'GSK' WHERE color_name = 'WILD CHERRY TINTCOAT';
UPDATE Colors SET rpo_code = 'GUI' WHERE color_name = 'ZEUS BRONZE METALLIC';
UPDATE Colors SET rpo_code = 'N/A' WHERE color_name = 'HYPERSONIC METALLIC';
