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
    engine_type VARCHAR(255) UNIQUE
);
SELECT * FROM Engines;

-- Transmissions Table
CREATE TABLE Transmissions (
    transmission_id SERIAL PRIMARY KEY,
    transmission_type VARCHAR(255) UNIQUE
);
SELECT * FROM transmissions;

-- Drivetrains Table
CREATE TABLE Drivetrains (
    drivetrain_id SERIAL PRIMARY KEY,
    drivetrain_type VARCHAR(255) UNIQUE
);
SELECT * FROM drivetrains;

-- Colors Table
CREATE TABLE Colors (
    color_id SERIAL PRIMARY KEY,
    color_name VARCHAR(255) UNIQUE
);
SELECT * FROM colors;

-- Dealers Table with sitedealer_code
CREATE TABLE Dealers (
    dealer_id SERIAL PRIMARY KEY,
    dealer_name VARCHAR(255),
    location VARCHAR(255),
    sitedealer_code VARCHAR(50)
);
SELECT * FROM dealers;

-- MMC Codes Table
CREATE TABLE MMC_Codes (
    mmc_code_id SERIAL PRIMARY KEY,
    mmc_code VARCHAR(50) UNIQUE
);

-- Orders Table
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE,
    creation_date DATE,
    mmc_code_id INTEGER REFERENCES MMC_Codes(mmc_code_id),
    sell_source VARCHAR(50),
    country VARCHAR(50)
);

-- Vehicles Table
CREATE TABLE Vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,
    modelYear INTEGER,
    model VARCHAR(255),
    body VARCHAR(255),
    trim VARCHAR(255),
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
    option_code VARCHAR(50)
);

-- Indexes for faster querying
CREATE INDEX idx_vehicle_vin ON Vehicles(vin);
CREATE INDEX idx_order_creation_date ON Orders(creation_date);
CREATE INDEX idx_option_vehicle_id ON options(vehicle_id);

-- Insert Engine Types
INSERT INTO Engines (engine_type) 
VALUES 
('6.2L (376 ci) V8 DI'), 
('6.2L SUPERCHARGED V8'), 
('3.6L V6, DI, VVT'), 
('2.0L Turbo, 4-cylinder, SIDI, VVT'), 
('3.0L TWIN TURBO V6, SIDI'), 
('2.7L TURBO'), 
('2.0L TURBO, 4-CYL, SIDI'), 
('3.6L V6 TWIN TURBO SIDI, DOHC, VVT'), 
('6.2L V8 DI'), 
('5.5L V8 DI');
SELECT * FROM Engines;

-- Insert Transmission Types
INSERT INTO transmissions (transmission_type) 
VALUES 
('A10'), 
('M6'), 
('A8'), 
('DCT8');
SELECT * FROM transmissions;

-- Insert Drivetrain Types
INSERT INTO drivetrains (drivetrain_type) 
VALUES 
('RWD'), 
('AWD');
SELECT * FROM drivetrains;

-- Insert Colors
INSERT INTO colors (color_name) 
VALUES 
('VIVID ORANGE METALLIC'),
('SUMMIT WHITE'),
('NITRO YELLOW METALLIC'),
('PANTHER BLACK MATTE'),
('RED HOT'),
('BLACK'),
('RADIANT RED TINTCOAT'),
('SHARKSKIN METALLIC'),
('RIVERSIDE BLUE METALLIC'),
('PANTHER BLACK METALLIC'),
('RIPTIDE BLUE METALLIC'),
('SATIN STEEL GREY METALLIC'),
('SHOCK'),
('CRUSH'),
('SHADOW GRAY METALLIC'),
('WILD CHERRY TINTCOAT'),
('GARNET RED TINTCOAT'),
('RALLY GREEN METALLIC'),
('RAPID BLUE'),
('BLACK RAVEN'),
('CRYSTAL WHITE TRICOAT'),
('MIDNIGHT STEEL METALLIC'),
('WAVE METALLIC'),
('ARGENT SILVER METALLIC'),
('VELOCITY RED'),
('CYBER YELLOW METALLIC'),
('COASTAL BLUE METALLIC'),
('BLACK DIAMOND TRICOAT'),
('MIDNIGHT SKY METALLIC'),
('MERCURY SILVER METALLIC'),
('RIFT METALLIC'),
('BLAZE METALLIC'),
('ELECTRIC BLUE'),
('MAVERICK NOIR FROST'),
('INFRARED TINTCOAT'),
('SATIN STEEL METALLIC'),
('SHADOW METALLIC'),
('GARNET METALLIC'),
('DARK EMERALD FROST'),
('EVERGREEN METALLIC'),
('DARK MOON METALLIC'),
('RED OBSESSION TINTCOAT'),
('ROYAL SPICE METALLIC'),
('SEBRING ORANGE'),
('ELKHART LAKE BLUE METALLIC'),
('ARCTIC WHITE'),
('TORCH RED'),
('CERAMIC MATRIX GRAY METALLIC'),
('ZEUS BRONZE METALLIC'),
('ACCELERATE YELLOW METALLIC'),
('LONG BEACH RED METALLIC'),
('BLADE SILVER METALLIC'),
('SILVER FLARE METALLIC'),
('RED MIST METALLIC TINTCOAT'),
('HYPERSONIC GRAY METALLIC'),
('AMPLIFY ORANGE TINTCOAT'),
('CAFFEINE METALLIC'),
('WHITE PEARL METALLIC TRICOAT'),
('CARBON FLASH METALLIC');
SELECT * FROM colors;

INSERT INTO Dealers (dealer_name, location, sitedealer_code)
SELECT DISTINCT 
    dealer, 
    location, 
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) AS sitedealer_code
FROM staging_allGM;
SELECT * FROM DEALERS;

-- Insert MMC Codes
INSERT INTO MMC_Codes (mmc_code)
SELECT DISTINCT JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')) AS mmc_code FROM staging_allGM;
SELECT * FROM MMC_CODES;

-- Insert orders
INSERT INTO Orders (order_number, creation_date, mmc_code_id, sell_source, country)
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
WHERE ordernum IS NOT NULL AND ordernum != '';
SELECT * FROM ORDERS;

-- Find/edit duplicates
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

SELECT
    JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.order_number')) AS order_number,
    COUNT(*) AS occurrences
FROM staging_allgm GROUP BY order_number HAVING occurrences > 1;

-- Insert Vehicles
INSERT INTO Vehicles (vin, modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, dealer_id, order_id)
SELECT vin, modelYear, model, body, trim,
    (SELECT engine_id FROM Engines WHERE engine_type = vehicleEngine) AS engine_id,
    (SELECT transmission_id FROM Transmissions WHERE transmission_type = transmission) AS transmission_id,
    (SELECT drivetrain_id FROM Drivetrains WHERE drivetrain_type = drivetrain) AS drivetrain_id,
    (SELECT color_id FROM Colors WHERE color_name = exterior_color) AS color_id,
    msrp,
    (SELECT dealer_id FROM Dealers WHERE dealer_name = dealer AND location = location AND sitedealer_code = JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.sitedealer_code')) LIMIT 1) AS dealer_id,
    (SELECT order_id FROM Orders WHERE order_number = ordernum) AS order_id
FROM staging_allGM;
select * from vehicles;

-- Insert Options with error handling
INSERT INTO Options (vehicle_id, option_code)
SELECT 
    v.vehicle_id,
    opt.option_value
FROM staging_allGM s
CROSS JOIN JSON_TABLE(
    JSON_EXTRACT(s.allJson, '$.Options'),
    '$[*]' COLUMNS(option_value VARCHAR(50) PATH '$')
) AS opt
JOIN Vehicles v ON v.vin = s.vin;
select * from options;
