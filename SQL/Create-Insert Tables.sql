create database vehicles;
use vehicles;
create user 'hussain' identified by 'Hussain92';
grant all privileges on vehicles.* to 'hussain'@'%';

-- staging_allGM
CREATE TABLE IF NOT EXISTS staging_allGM (
	vin varchar(17) PRIMARY KEY,
    modelYear int,
    model varchar(75),
    body varchar(20),
    trim varchar(25),
    vehicleEngine varchar(75),
    transmission varchar(4),
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
    color_name VARCHAR(64) UNIQUE,
    rpo_code VARCHAR(3)
);

-- Dealers Table with sitedealer_code
CREATE TABLE Dealers (
    dealer_id SERIAL PRIMARY KEY,
    dealer_name VARCHAR(64),
    location VARCHAR(64),
    sitedealer_code VARCHAR(5)
    UNIQUE KEY idx_dealer_unique (dealer_name, location, sitedealer_code)
);

-- MMC Codes Table
CREATE TABLE MMC_Codes (
    mmc_code_id SERIAL PRIMARY KEY,
    mmc_code VARCHAR(7) UNIQUE
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

-- INSERT DATA INTO TABLES --

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
INSERT IGNORE INTO Dealers (dealer_name, location, sitedealer_code)
SELECT DISTINCT 
    dealer, 
    location, 
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) AS sitedealer_code
FROM staging_allGM;

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

-- Insert SpecialEditions
INSERT IGNORE INTO SpecialEditions (vehicle_id, special_desc)
SELECT v.vehicle_id, special_desc
FROM Vehicles v
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
    UNION ALL SELECT 'ZTK', 'ZTK Track Performance Package'
    UNION ALL SELECT 'Z6X', 'Extreme Off-Road Package'
    UNION ALL SELECT 'WFP', 'Omega Edition'
) AS special_map ON opt.option_code = special_map.rpo_code
WHERE NOT EXISTS (
    SELECT 1
    FROM SpecialEditions se 
    WHERE se.vehicle_id = v.vehicle_id 
    AND se.special_desc = special_map.special_desc
);

-- Add ZLZ dual-meaning special edition logic
INSERT IGNORE INTO SpecialEditions (vehicle_id, special_desc)
SELECT 
    v.vehicle_id,
    CASE
        WHEN v.model = 'CT4' AND opt.option_code = 'ZLZ' THEN 'Petit Pataud Special Edition'
        WHEN v.model = 'CT5' AND opt.option_code = 'ZLZ' THEN 'Le Monstre Special Edition'
    END AS special_desc
FROM Vehicles v
JOIN Options opt ON v.vehicle_id = opt.vehicle_id
WHERE opt.option_code = 'ZLZ'
  AND v.model IN ('CT4','CT5')
  AND NOT EXISTS (
        SELECT 1
        FROM SpecialEditions se
        WHERE se.vehicle_id = v.vehicle_id
          AND se.special_desc = 
                CASE
                    WHEN v.model = 'CT4' THEN 'Petit Pataud Special Edition'
                    ELSE 'Le Monstre Special Edition'
                END
    );

select * from SpecialEditions;

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
    WHERE v.color_id = 17
      AND se.special_desc LIKE '%Garage 56 Special Edition%'
)
UPDATE SpecialEditions se
JOIN OrderedEditions oe ON se.vehicle_id = oe.vehicle_id
SET se.special_desc = CONCAT('Garage 56 Special Edition #', LPAD(oe.row_num, 2, '0'));

-- Update Stats for new colors (after doing all new inserts)
UPDATE Colors SET rpo_code = 'G4Z' WHERE color_name = 'ROSWELL GREEN METALLIC';
UPDATE Colors SET rpo_code = 'GD0' WHERE color_name = 'ACCELERATE YELLOW METALLIC';
UPDATE Colors SET rpo_code = 'GC5' WHERE color_name = 'AMPLIFY ORANGE TINTCOAT';
UPDATE Colors SET rpo_code = 'G8G' WHERE color_name = 'ARCTIC WHITE';
UPDATE Colors SET rpo_code = 'GXD' WHERE color_name = 'ARGENT SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GLK' WHERE color_name = 'BLACK DIAMOND TRICOAT';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'BLACK RAVEN';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'BLACK';
UPDATE Colors SET rpo_code = 'GAN' WHERE color_name = 'BLADE SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GCF' WHERE color_name = 'BLAZE ORANGE METALLIC';
UPDATE Colors SET rpo_code = 'GVR' WHERE color_name = 'CACTI GREEN';
UPDATE Colors SET rpo_code = 'G48' WHERE color_name = 'CAFFEINE METALLIC';
UPDATE Colors SET rpo_code = 'GAR' WHERE color_name = 'CARBON FLASH METALLIC';
UPDATE Colors SET rpo_code = 'G9F' WHERE color_name = 'CERAMIC MATRIX GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GJV' WHERE color_name = 'COASTAL BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GBK' WHERE color_name = 'COMPETITION YELLOW TINTCOAT';
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
UPDATE Colors SET rpo_code = 'G1E' WHERE color_name = 'LONG BEACH RED METALLIC TINTCOAT';
UPDATE Colors SET rpo_code = 'GCI' WHERE color_name = 'MANHATTAN NOIR METALLIC';
UPDATE Colors SET rpo_code = 'GNW' WHERE color_name = 'MAVERICK NOIR FROST';
UPDATE Colors SET rpo_code = 'GKA' WHERE color_name = 'MERCURY SILVER METALLIC';
UPDATE Colors SET rpo_code = 'GXF' WHERE color_name = 'MIDNIGHT SKY METALLIC';
UPDATE Colors SET rpo_code = 'GXU' WHERE color_name = 'MIDNIGHT STEEL METALLIC';
UPDATE Colors SET rpo_code = 'GCP' WHERE color_name = 'NITRO YELLOW METALLIC';
UPDATE Colors SET rpo_code = 'GNW' WHERE color_name = 'PANTHER BLACK MATTE';
UPDATE Colors SET rpo_code = 'GLK' WHERE color_name = 'PANTHER BLACK METALLIC TINTCOAT';
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
UPDATE Colors SET rpo_code = 'G26' WHERE color_name = 'SEBRING ORANGE TINTCOAT';
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
UPDATE Colors SET rpo_code = 'GTR' WHERE color_name = 'ADMIRAL BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GC6' WHERE color_name = 'CORVETTE RACING YELLOW TINTCOAT';
UPDATE Colors SET rpo_code = 'GB8' WHERE color_name = 'MOSAIC BLACK METALLIC';
UPDATE Colors SET rpo_code = 'GAN' WHERE color_name = 'SILVER ICE METALLIC';
UPDATE Colors SET rpo_code = 'G7Q' WHERE color_name = 'WATKINS GLEN GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GAZ' WHERE color_name = 'INTERSTELLAR WHITE';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'VOID BLACK';
UPDATE Colors SET rpo_code = 'GNO' WHERE color_name = 'METEORITE METALLIC';
UPDATE Colors SET rpo_code = 'GXN' WHERE color_name = 'DEEP AURORA METALLIC';
UPDATE Colors SET rpo_code = 'GC5' WHERE color_name = 'AFTERBURNER TINTCOAT';
UPDATE Colors SET rpo_code = 'G7X' WHERE color_name = 'TIDE METALLIC';
UPDATE Colors SET rpo_code = 'GKK' WHERE color_name = 'SUPERNOVA METALLIC';
UPDATE Colors SET rpo_code = 'GNO' WHERE color_name = 'METEORITE METALLIC';
UPDATE Colors SET rpo_code = 'GC5' WHERE color_name = 'AFTERBURNER TINTCOAT';
UPDATE Colors SET rpo_code = 'G7X' WHERE color_name = 'TIDE METALLIC';
UPDATE Colors SET rpo_code = 'GKK' WHERE color_name = 'SUPERNOVA METALLIC';
UPDATE Colors SET rpo_code = 'GXN' WHERE color_name = 'DEEP AURORA METALLIC';
UPDATE Colors SET rpo_code = 'G7W' WHERE color_name = 'MOONSHOT GREEN MATTE';
UPDATE Colors SET rpo_code = 'GLG' WHERE color_name = 'NEPTUNE BLUE MATTE';
UPDATE Colors SET rpo_code = 'GNO' WHERE color_name = 'SLATE GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GLG' WHERE color_name = 'ZEPHYR BLUE MATTE METALLIC';
UPDATE Colors SET rpo_code = 'GAI' WHERE color_name = 'BLUE SMOKE METALLIC';
UPDATE Colors SET rpo_code = 'GAG' WHERE color_name = 'HABANERO ORANGE';
UPDATE Colors SET rpo_code = 'GNO' WHERE color_name = 'THUNDERSTORM GRAY';
UPDATE Colors SET rpo_code = 'GBA' WHERE color_name = 'ONYX BLACK';
UPDATE Colors SET rpo_code = 'GAI' WHERE color_name = 'DEEP OCEAN METALLIC';
UPDATE Colors SET rpo_code = 'GAB' WHERE color_name = 'DARK EMBER TINTCOAT';
UPDATE Colors SET rpo_code = 'GLG' WHERE color_name = 'MOONLIGHT MATTE';
UPDATE Colors SET rpo_code = 'GSJ' WHERE color_name = 'FLARE METALLIC';
UPDATE Colors SET rpo_code = 'GAB' WHERE color_name = 'BLACK CHERRY TINTCOAT';
UPDATE Colors SET rpo_code = 'GLG' WHERE color_name = 'MIDNIGHT STEEL FROST';
UPDATE Colors SET rpo_code = 'G42' WHERE color_name = 'SANDSTONE';
UPDATE Colors SET rpo_code = 'G4J' WHERE color_name = 'VIBRANT WHITE TRICOAT';
UPDATE Colors SET rpo_code = 'GAG' WHERE color_name = 'MONARCH ORANGE';
UPDATE Colors SET rpo_code = 'GBL' WHERE color_name = 'MAGNUS METAL FROST';
UPDATE Colors SET rpo_code = 'GNO' WHERE color_name = 'LUNA METALLIC';
UPDATE Colors SET rpo_code = 'GNR' WHERE color_name = 'ADOBE FROST';
UPDATE Colors SET rpo_code = 'GAI' WHERE color_name = 'GRAPHITE BLUE METALLIC';
UPDATE Colors SET rpo_code = 'GAG' WHERE color_name = 'SOLAR ORANGE';
UPDATE Colors SET rpo_code = 'GBW' WHERE color_name = 'TYPHOON METALLIC';
UPDATE Colors SET rpo_code = 'GAE' WHERE color_name = 'DRIFT METALLIC';
UPDATE Colors SET rpo_code = 'GBL' WHERE color_name = 'MAGNUS METAL FROST';
UPDATE Colors SET rpo_code = 'G4Z' WHERE color_name = 'ROSWELL GREEN METALLIC';
UPDATE Colors SET rpo_code = 'GMU' WHERE color_name = 'BRONZE DUNE METALLIC';
UPDATE Colors SET rpo_code = 'G6M' WHERE color_name = 'GALACTIC GRAY METALLIC';
UPDATE Colors SET rpo_code = 'GBD' WHERE color_name = 'AEGEAN STONE';
UPDATE Colors SET rpo_code = 'GXP' WHERE color_name = 'DEEP SEA METALLIC';
UPDATE Colors SET rpo_code = 'G5D' WHERE color_name = 'LATTE METALLIC';

UPDATE Colors SET rpo_code = 'G' WHERE color_name = '';
SELECT * FROM Colors;

-- Set Engine RPO
select * from Engines;
update Engines SET engine_rpo = "L87" WHERE engine_id = 20;

select * from Vehicles;
