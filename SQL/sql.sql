CREATE DATABASE vehicles;
USE vehicles;

DROP TABLE gm;
CREATE TABLE IF NOT EXISTS gm (
	vin varchar(17),
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

SELECT * FROM gm
ORDER BY RAND()
LIMIT 10;

SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(location, ',', -1), ' ', 2) AS state_province, COUNT(*) AS count FROM gm
WHERE model = 'CT5'
GROUP BY state_province
ORDER BY count DESC;

SELECT * FROM gm
WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(location, ',', -1), ' ', 2) = ' PR';

SELECT * FROM gm
WHERE trim = 'V-SERIES BLACKWING' AND
allJson->'$.maker' = 'CADILLAC'
ORDER BY msrp DESC;

INSERT INTO gm VALUES ("1G6DP5RK0L0117423","2020","CT5","SEDAN","SPORT","2.0L TURBO, 4-CYL, SIDI","A10","RWD","SATIN STEEL METALLIC","49530","EVERETT CADILLAC","HICKORY, NC 28603-1928","XFJZ9F",'{"maker": "CADILLAC", "model_year": "2020", "mmc_code": "6DD79", "vin": "1G6DP5RK0L0117423", "sitedealer_code": "25728", "sell_source": "12", "order_number": "XFJZ9F", "creation_date": "2/8/2020", "Options": ["AEF", "AER", "AF6", "AHC", "AHE", "AHF", "AHH", "AHP", "AJC", "AJW", "AKE", "AKP", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "CE1", "CJ2", "C3U", "C70", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "G9K", "HRD", "HS1", "H2X", "IOT", "I20", "JF5", "JJ2", "JM8", "J56", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KU9", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "MHS", "NEA", "NE8", "NK4", "NTB", "N37", "QBJ", "Q82", "RWL", "R8R", "R9N", "SLM", "TDM", "TFK", "TTW", "T4L", "UD7", "UEU", "UE1", "UFG", "UGC", "UGE", "UG1", "UHS", "UHY", "UJN", "UKC", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WML", "XL8", "YM8", "Y26", "Y5V", "Y5W", "Y6F", "0ST", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "8X2", "9L3", "9X2"]}');

-- Original "{'maker': 'CADILLAC', 'model_year': '2020', 'mmc_code': ' 6DD79', 'vin': '1G6DP5RK0L0117423', 'sitedealer_code': ' 25728', 'sell_source': '12', 'order_number': 'XFJZ9F', 'creation_date': '2/8/2020', 'Options': ['AEF', 'AER', 'AF6', 'AHC', 'AHE', 'AHF', 'AHH', 'AHP', 'AJC', 'AJW', 'AKE', 'AKP', 'AL0', 'AM9', 'AQ9', 'ATH', 'AT8', 'AVK', 'AVN', 'AVU', 'AXG', 'AXJ', 'AYG', 'A2X', 'A45', 'A7K', 'BTV', 'BYO', 'B34', 'B35', 'B6A', 'CE1', 'CJ2', 'C3U', 'C70', 'C73', 'DD8', 'DEG', 'DMB', 'D52', 'D75', 'EF7', 'EPH', 'E22', 'E28', 'FE2', 'FE9', 'FJW', 'G9K', 'HRD', 'HS1', 'H2X', 'IOT', 'I20', 'JF5', 'JJ2', 'JM8', 'J56', 'J77', 'KA1', 'KB7', 'KD4', 'KI3', 'KL9', 'KPA', 'KRV', 'KU9', 'K12', 'K34', 'K4C', 'LAL', 'LSY', 'MAH', 'MCR', 'MDB', 'MHS', 'NEA', 'NE8', 'NK4', 'NTB', 'N37', 'QBJ', 'Q82', 'RWL', 'R8R', 'R9N', 'SLM', 'TDM', 'TFK', 'TTW', 'T4L', 'UD7', 'UEU', 'UE1', 'UFG', 'UGC', 'UGE', 'UG1', 'UHS', 'UHY', 'UJN', 'UKC', 'UKJ', 'UMN', 'UQP', 'USS', 'UVB', 'U2K', 'U2L', 'U80', 'VHM', 'VH9', 'VLI', 'VRF', 'VRG', 'VRH', 'VRJ', 'VRK', 'VRL', 'VRM', 'VRN', 'VRR', 'VTI', 'VT7', 'VV4', 'V76', 'V8D', 'WML', 'XL8', 'YM8', 'Y26', 'Y5V', 'Y5W', 'Y6F', '0ST', '1NF', '1SE', '1SZ', '2NF', '2ST', '4AA', '5A7', '5FC', '6X1', '7X1', '8X2', '9L3', '9X2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']}"
-- Modified '{"maker": "CADILLAC", "model_year": "2020", "mmc_code": "6DD79", "vin": "1G6DP5RK0L0117423", "sitedealer_code": "25728", "sell_source": "12", "order_number": "XFJZ9F", "creation_date": "2/8/2020", "Options": ["AEF", "AER", "AF6", "AHC", "AHE", "AHF", "AHH", "AHP", "AJC", "AJW", "AKE", "AKP", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "CE1", "CJ2", "C3U", "C70", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "G9K", "HRD", "HS1", "H2X", "IOT", "I20", "JF5", "JJ2", "JM8", "J56", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KU9", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "MHS", "NEA", "NE8", "NK4", "NTB", "N37", "QBJ", "Q82", "RWL", "R8R", "R9N", "SLM", "TDM", "TFK", "TTW", "T4L", "UD7", "UEU", "UE1", "UFG", "UGC", "UGE", "UG1", "UHS", "UHY", "UJN", "UKC", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WML", "XL8", "YM8", "Y26", "Y5V", "Y5W", "Y6F", "0ST", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "8X2", "9L3", "9X2"]}'
-- Has to not have empty values ('', '', '') and swap ' & " around. Cleaned empty strings in mmc_code and sitedealer_code.
INSERT INTO gm (allJson) VALUES ('{"maker": "CADILLAC", "model_year": "2020", "mmc_code": "6DD79", "vin": "1G6DP5RK0L0117423", "sitedealer_code": "25728", "sell_source": "12", "order_number": "XFJZ9F", "creation_date": "2/8/2020", "Options": ["AEF", "AER", "AF6", "AHC", "AHE", "AHF", "AHH", "AHP", "AJC", "AJW", "AKE", "AKP", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "CE1", "CJ2", "C3U", "C70", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "G9K", "HRD", "HS1", "H2X", "IOT", "I20", "JF5", "JJ2", "JM8", "J56", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KU9", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "MHS", "NEA", "NE8", "NK4", "NTB", "N37", "QBJ", "Q82", "RWL", "R8R", "R9N", "SLM", "TDM", "TFK", "TTW", "T4L", "UD7", "UEU", "UE1", "UFG", "UGC", "UGE", "UG1", "UHS", "UHY", "UJN", "UKC", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WML", "XL8", "YM8", "Y26", "Y5V", "Y5W", "Y6F", "0ST", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "8X2", "9L3", "9X2"]}');

-- Original "['AEF', 'AER', 'AF6', 'AHC', 'AHE', 'AHF', 'AHH', 'AHP', 'AJC', 'AJW', 'AKE', 'AKP', 'AL0', 'AM9', 'AQ9', 'ATH', 'AT8', 'AVK', 'AVN', 'AVU', 'AXG', 'AXJ', 'AYG', 'A2X', 'A45', 'A7K', 'BTV', 'BYO', 'B34', 'B35', 'B6A', 'CE1', 'CJ2', 'C3U', 'C70', 'C73', 'DD8', 'DEG', 'DMB', 'D52', 'D75', 'EF7', 'EPH', 'E22', 'E28', 'FE2', 'FE9', 'FJW', 'G9K', 'HRD', 'HS1', 'H2X', 'IOT', 'I20', 'JF5', 'JJ2', 'JM8', 'J56', 'J77', 'KA1', 'KB7', 'KD4', 'KI3', 'KL9', 'KPA', 'KRV', 'KU9', 'K12', 'K34', 'K4C', 'LAL', 'LSY', 'MAH', 'MCR', 'MDB', 'MHS', 'NEA', 'NE8', 'NK4', 'NTB', 'N37', 'QBJ', 'Q82', 'RWL', 'R8R', 'R9N', 'SLM', 'TDM', 'TFK', 'TTW', 'T4L', 'UD7', 'UEU', 'UE1', 'UFG', 'UGC', 'UGE', 'UG1', 'UHS', 'UHY', 'UJN', 'UKC', 'UKJ', 'UMN', 'UQP', 'USS', 'UVB', 'U2K', 'U2L', 'U80', 'VHM', 'VH9', 'VLI', 'VRF', 'VRG', 'VRH', 'VRJ', 'VRK', 'VRL', 'VRM', 'VRN', 'VRR', 'VTI', 'VT7', 'VV4', 'V76', 'V8D', 'WML', 'XL8', 'YM8', 'Y26', 'Y5V', 'Y5W', 'Y6F', '0ST', '1NF', '1SE', '1SZ', '2NF', '2ST', '4AA', '5A7', '5FC', '6X1', '7X1', '8X2', '9L3', '9X2']"
-- Moddified '["AEF", "AER", "AF6", "AHC", "AHE", "AHF", "AHH", "AHP", "AJC", "AJW", "AKE", "AKP", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "CE1", "CJ2", "C3U", "C70", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "G9K", "HRD", "HS1", "H2X", "IOT", "I20", "JF5", "JJ2", "JM8", "J56", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KU9", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "MHS", "NEA", "NE8", "NK4", "NTB", "N37", "QBJ", "Q82", "RWL", "R8R", "R9N", "SLM", "TDM", "TFK", "TTW", "T4L", "UD7", "UEU", "UE1", "UFG", "UGC", "UGE", "UG1", "UHS", "UHY", "UJN", "UKC", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WML", "XL8", "YM8", "Y26", "Y5V", "Y5W", "Y6F", "0ST", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "8X2", "9L3", "9X2"]'
-- Swap ' & " around.
-- INSERT INTO gm (allRpos) VALUES ('["AEF", "AER", "AF6", "AHC", "AHE", "AHF", "AHH", "AHP", "AJC", "AJW", "AKE", "AKP", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "CE1", "CJ2", "C3U", "C70", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "EPH", "E22", "E28", "FE2", "FE9", "FJW", "G9K", "HRD", "HS1", "H2X", "IOT", "I20", "JF5", "JJ2", "JM8", "J56", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KU9", "K12", "K34", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "MHS", "NEA", "NE8", "NK4", "NTB", "N37", "QBJ", "Q82", "RWL", "R8R", "R9N", "SLM", "TDM", "TFK", "TTW", "T4L", "UD7", "UEU", "UE1", "UFG", "UGC", "UGE", "UG1", "UHS", "UHY", "UJN", "UKC", "UKJ", "UMN", "UQP", "USS", "UVB", "U2K", "U2L", "U80", "VHM", "VH9", "VLI", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VTI", "VT7", "VV4", "V76", "V8D", "WML", "XL8", "YM8", "Y26", "Y5V", "Y5W", "Y6F", "0ST", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "8X2", "9L3", "9X2"]');
-- Old, deleting allRpos column.

-- Importing .txt
LOAD DATA LOCAL INFILE 'C:/Users/Hussa/OneDrive/Desktop/camaro20-24/test.txt'
INTO TABLE gm COLUMNS TERMINATED BY '\t';
-- Found issues when importing .csv (N/A values messed up everything, replace with empty or {} for allJson's JSON type)

-- How to access options from allJson without allRpos column
SELECT * FROM gm
WHERE JSON_CONTAINS(allJson->'$.Options', '["A1Y"]')
AND JSON_CONTAINS(allJson->'$.Options', '["GJ0"]')
ORDER BY msrp DESC;

-- Select distinct values
SELECT DISTINCT allJson->'$.maker' AS maker
FROM gm
ORDER BY maker;

SELECT allJson->'$.maker' AS maker, modelYear, COUNT(*) AS count
FROM gm
GROUP BY allJson->'$.maker', modelYear
ORDER BY count DESC;

SELECT *
FROM gm
WHERE location LIKE '%, % %' AND
-- exterior_color = 'RIPTIDE BLUE METALLIC' AND
      (
          -- Match Canadian locations (Province abbreviations and postal codes)
          location LIKE '%, AB %' OR
          location LIKE '%, BC %' OR
          location LIKE '%, GU %' OR -- USA Territory
          location LIKE '%, MB %' OR
          location LIKE '%, NF %' OR
          location LIKE '%, NT %' OR
          location LIKE '%, ON %' OR
          location LIKE '%, PE %' OR
          location LIKE '%, PQ %' OR
          location LIKE '%, PR %' OR -- USA Territory
          location LIKE '%, SK %'
      )
ORDER BY msrp DESC;

SELECT allJson->'$.maker' AS maker, 
       modelYear,
       COUNT(*) AS count
FROM gm
WHERE allJson->'$.maker' = 'CADILLAC'
GROUP BY allJson->'$.maker', modelYear
ORDER BY count DESC;

SELECT * FROM gm
WHERE allJson->'$.maker' = 'CADILLAC'
AND modelYear = 2021;

