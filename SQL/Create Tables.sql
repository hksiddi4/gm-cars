create database vehicles;
use vehicles;
create user 'hussain' identified by 'Hussain92';
grant all privileges on vehicles.* to 'hussain'@'%';

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
DROP TABLE staging_allGM;
SELECT * FROM staging_allGM;

-- Engines Table
CREATE TABLE Engines (
    engine_id SERIAL PRIMARY KEY,
    engine_type VARCHAR(48) UNIQUE
);
SELECT * FROM Engines;
DROP TABLE engines;

-- Transmissions Table
CREATE TABLE Transmissions (
    transmission_id SERIAL PRIMARY KEY,
    transmission_type VARCHAR(4) UNIQUE
);
SELECT * FROM transmissions;
DROP TABLE transmissions;

-- Drivetrains Table
CREATE TABLE Drivetrains (
    drivetrain_id SERIAL PRIMARY KEY,
    drivetrain_type VARCHAR(3) UNIQUE
);
SELECT * FROM drivetrains;
DROP TABLE drivetrains;

-- Colors Table
CREATE TABLE Colors (
    color_id SERIAL PRIMARY KEY,
    color_name VARCHAR(32) UNIQUE
);
SELECT * FROM colors;
DROP TABLE colors;

-- Dealers Table with sitedealer_code
CREATE TABLE Dealers (
    dealer_id SERIAL PRIMARY KEY,
    dealer_name VARCHAR(64),
    location VARCHAR(64),
    sitedealer_code VARCHAR(5)
);
SELECT * FROM dealers;
DROP TABLE dealers;

-- MMC Codes Table
CREATE TABLE MMC_Codes (
    mmc_code_id SERIAL PRIMARY KEY,
    mmc_code VARCHAR(5) UNIQUE
);
SELECT * FROM mmc_codes;
DROP TABLE mmc_codes;

-- Orders Table
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(6) UNIQUE,
    creation_date DATE,
    mmc_code_id INTEGER REFERENCES MMC_Codes(mmc_code_id),
    sell_source VARCHAR(2),
    country VARCHAR(8)
);
SELECT * FROM orders;
DROP TABLE orders;

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
SELECT * FROM vehicles;
DROP TABLE vehicles;

-- Options Table
CREATE TABLE Options (
    option_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES Vehicles(vehicle_id),
    option_code VARCHAR(3),
    UNIQUE (vehicle_id, option_code)
);
DROP TABLE Options;

-- Special Editions Table
CREATE TABLE SpecialEditions (
	special_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES Vehicles(vehicle_id),
    special_desc VARCHAR(64)
);
DROP TABLE specialeditions;

-- Indexes for faster querying
-- Composite Index for Frequent Filtering and Grouping
CREATE INDEX idx_vehicle_model_info
ON Vehicles(modelYear, model, body, trim);
CREATE INDEX idx_vehicle_performance_info
ON Vehicles(engine_id, transmission_id, drivetrain_id, color_id, msrp, order_id, dealer_id);
-- Index for VIN (unique and commonly queried)
CREATE INDEX idx_vehicle_vin ON Vehicles(vin);
-- Index for SpecialEditions table (left join optimization and GROUP_CONCAT)
CREATE INDEX idx_special_edition_vehicle
ON SpecialEditions(vehicle_id, special_desc);
-- Index for Sorting and Filtering on modelYear, engine_id, and msrp
CREATE INDEX idx_vehicle_filter_sort
ON Vehicles(modelYear, engine_id, msrp, model);
-- Foreign Key Indexes for Faster Joins in the Vehicles table
CREATE INDEX idx_vehicle_engine_id ON Vehicles(engine_id);
CREATE INDEX idx_vehicle_transmission_id ON Vehicles(transmission_id);
CREATE INDEX idx_vehicle_drivetrain_id ON Vehicles(drivetrain_id);
CREATE INDEX idx_vehicle_color_id ON Vehicles(color_id);
CREATE INDEX idx_vehicle_order_id ON Vehicles(order_id);
CREATE INDEX idx_vehicle_dealer_id ON Vehicles(dealer_id);
-- Orders Table (index on creation_date for faster date-based queries)
CREATE INDEX idx_order_creation_date ON Orders(creation_date);
-- Options Table (composite index for vehicle_id and option_code)
CREATE INDEX idx_options_vehicle_code ON Options(vehicle_id, option_code);
CREATE INDEX idx_vehicle_distinct_fields
ON Vehicles(modelYear, model, body, `trim`, engine_id, transmission_id, color_id, order_id);
CREATE INDEX idx_special_editions ON SpecialEditions(vehicle_id, special_desc);


CREATE INDEX idx_vehicle_modelYear ON Vehicles(modelYear);
CREATE INDEX idx_vehicle_composite ON Vehicles(vin, modelYear, engine_id, transmission_id, drivetrain_id, color_id, order_id, dealer_id);

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

INSERT INTO Dealers (dealer_name, location, sitedealer_code)
SELECT DISTINCT 
    dealer, 
    location, 
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) AS sitedealer_code
FROM staging_allGM
WHERE (dealer, location, JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code'))) 
      NOT IN (SELECT dealer_name, location, sitedealer_code FROM Dealers);
SELECT * FROM Dealers ORDER BY SITEDEALER_CODE;

SELECT
    sitedealer_code,
    COUNT(*) AS occurrences
FROM Dealers GROUP BY sitedealer_code HAVING occurrences > 1;

SELECT * FROM Dealers WHERE sitedealer_code = '09915';

SELECT v.* 
FROM Vehicles v
JOIN Dealers d ON v.dealer_id = d.dealer_id
WHERE d.sitedealer_code = '16173';

-- Insert MMC Codes
INSERT IGNORE INTO MMC_Codes (mmc_code)
SELECT DISTINCT REPLACE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')), ' ', '') AS mmc_code 
FROM staging_allGM
WHERE REPLACE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')), ' ', '') NOT IN (SELECT mmc_code FROM MMC_Codes);
SELECT * FROM MMC_CODES;

-- Insert orders
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
SELECT * FROM ORDERS;

-- Find/edit duplicates
	SELECT
		JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.order_number')) AS order_number,
		COUNT(*) AS occurrences
	FROM staging_allgm GROUP BY order_number HAVING occurrences > 1;

	SELECT COUNT(vin) FROM vehicles;

	UPDATE staging_allgm
	SET
	TRIM = 'LUXURY',
	VEHICLEENGINE = '2.0L TURBO, 4-CYL, SIDI',
	DRIVETRAIN = 'RWD',
	EXTERIOR_COLOR = 'BLACK RAVEN',
	MSRP = '41710',
	DEALER = 'CENTRAL CADILLAC',
	LOCATION = 'JONESBORO, AR 72403-6600',
	ORDERNUM = 'XXKDJ3',
	allJson = '{"maker":"CADILLAC", "model_year":"2021", "mmc_code":"6DB79", "vin":"1G6DW5RK1M0108427", "sitedealer_code":"17270", "sell_source": "12", "order_number": "XXKDJ3", "creation_date":"10/9/2020", "Options":["AEF", "AER", "AHP", "AJC", "AJW", "AKP", "AL0", "AL9", "AM9", "AQ9", "ATH", "AT8", "AT9", "AVN", "AXG", "AXJ", "AYG", "A2X", "A7J", "BTV", "BYO", "B34", "B35", "B56", "CE1", "CJ2", "C3U", "DEG", "DWK", "D31", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "GBA", "HRD", "HS1", "H2G", "IOT", "JJ2", "JL9", "JM8", "J21", "J77", "KA1", "KBC", "KD4", "KI3", "KL9", "KPA", "KRV", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDE", "MHS", "NB9", "NE8", "NP5", "NTB", "N37", "PCM", "PPW", "QBC", "Q81", "RWL", "RYT", "R6R", "R7E", "R8R", "R9N", "SLM", "S08", "TDM", "TFK", "TTW", "T4L", "T8Z", "UDD", "UEU", "UE1", "UGC", "UGE", "UG1", "UHY", "UIT", "UJN", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VK3", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WMU", "XL8", "YM8", "Y19", "Y26", "Y5V", "0ST", "1NF", "1SB", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "719", "8X2", "9L3", "9X2"]}'
	WHERE vin = '1G6DW5RK1M0108427';
	SELECT * FROM staging_allgm WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.order_number')) = 'ZDMJR6';

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
select * from vehicles;

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
commit;

SELECT se.special_desc, v.vin
FROM SpecialEditions se
JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
WHERE v.vin = '1G1FJ1R6XR0100021';

UPDATE SpecialEditions se
JOIN Vehicles v ON se.vehicle_id = v.vehicle_id
SET se.special_desc = 'Hertz / Hendrick Motorsports Edition #001'
WHERE v.vin = '1G1FH1R70L0105904';
