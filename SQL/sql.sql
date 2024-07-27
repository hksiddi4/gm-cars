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
-- JSON data must be formatted "{""item"": ""value""}"
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
WHERE JSON_CONTAINS(allJson->'$.Options', '["A1Z"]')
ORDER BY msrp DESC;

-- Select distinct values
SELECT DISTINCT allJson->'$.maker' AS maker
FROM gm
ORDER BY maker;

-- Select distinct values
SELECT DISTINCT exterior_color
FROM gm ORDER BY exterior_color;

SELECT allJson->'$.maker' AS maker, modelYear, COUNT(*) AS count
FROM gm
GROUP BY allJson->'$.maker', modelYear
ORDER BY count DESC;

SELECT *
FROM gm
WHERE location LIKE '%, % %' AND
      (
          -- Match Canadian locations (Province abbreviations and postal codes)
          location LIKE '%, AB %' OR
          location LIKE '%, BC %' OR
          location LIKE '%, MB %' OR
          location LIKE '%, NB %' OR
          location LIKE '%, NF %' OR
          location LIKE '%, NS %' OR
          location LIKE '%, NT %' OR
          location LIKE '%, ON %' OR
          location LIKE '%, PE %' OR
          location LIKE '%, PQ %' OR
          location LIKE '%, SK %'
      )
ORDER BY msrp DESC;

SELECT * FROM gm WHERE JSON_CONTAINS(allJson->'$.maker', '"GMCANADA"');

SELECT allJson->'$.maker' AS maker, 
       modelYear,
       COUNT(*) AS count
FROM gm
WHERE allJson->'$.maker' = 'CADILLAC'
GROUP BY allJson->'$.maker', modelYear
ORDER BY count DESC;

SELECT JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) AS Options, COUNT(*) AS Count
FROM gm
GROUP BY Options
HAVING COUNT(*) > 1
ORDER by Count DESC;

SELECT COUNT(*) AS Count
FROM gm
WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) = '1SV';

SELECT COUNT(*) AS Count
FROM gm
WHERE trim = 'V-SERIES BLACKWING' AND model = 'CT5';

SELECT * FROM gm WHERE trim = '1LZ';

UPDATE gm SET trim = 'LT1' WHERE trim = '1LZ';

SELECT COUNT(*) AS Count FROM gm WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) = '["AEF", "AEQ", "AF6", "AHC", "AHE", "AHF", "AHH", "AJC", "AJW", "AKE", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A69", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "B70", "CE1", "CF5", "CJ2", "C59", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "E22", "E28", "FE2", "FJW", "F46", "GJI", "HRD", "HS1", "H2X", "IOT", "JE5", "JF5", "JJ2", "JM8", "J22", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KSG", "KU9", "K12", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "M5N", "NB9", "NE1", "NE8", "NK4", "NUG", "N37", "PPW", "PZJ", "Q4D", "RFD", "RSR", "R6M", "R6W", "R9N", "SLM", "TDM", "TFK", "TQ5", "TSQ", "TTW", "T4L", "T8Z", "UC3", "UDD", "UD5", "UEU", "UE1", "UE4", "UFG", "UGE", "UGN", "UG1", "UHX", "UIT", "UJN", "UKC", "UKJ", "UMN", "UQS", "UVB", "UVZ", "U2K", "U2L", "U80", "VHM", "VH9", "VK3", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VT7", "VV4", "V76", "V8D", "WMW", "XL8", "Y26", "Y5X", "Y5Y", "Y6F", "0ST", "00G", "00Z", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "719", "8X2", "9L3", "9X2"]';
