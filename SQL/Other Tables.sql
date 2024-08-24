SELECT * FROM gm
WHERE vin = '1G1FH1R78N0102770';

SELECT * FROM gm WHERE model IN ('Camaro','CT4') ORDER BY msrp DESC;

SELECT * FROM gm ORDER BY RAND() LIMIT 25;

-- Find duplicate options
SELECT JSON_EXTRACT(allJson, '$.Options') AS Options, COUNT(*) as Count
FROM gm
GROUP BY JSON_EXTRACT(allJson, '$.Options')
HAVING COUNT(*) > 1
ORDER BY Count DESC;

SELECT * FROM gm WHERE model = 'CAMARO' AND exterior_color = 'PANTHER BLACK MATTE' ORDER BY SUBSTRING(vin, -6);

UPDATE gm
SET exterior_color = 'PANTHER BLACK MATTE'
WHERE model = 'CAMARO' AND
exterior_color = 'PANTHER BLACK METALLIC' AND
trim = 'ZL1';

UPDATE gm
SET exterior_color = 'ZEUS BRONZE METALLIC'
WHERE exterior_color = 'ZEUS BRONZE';

SELECT * FROM gm
WHERE JSON_CONTAINS(allJson->'$.Options', '"ZCR"');
  #AND JSON_CONTAINS(allJson->'$.maker', '"GMCANADA"')
  #AND location LIKE '%PQ%';

SELECT trim, model, COUNT(*) as Count FROM gm
WHERE model = 'CORVETTE' AND modelYear = '2020'
GROUP BY trim;

SELECT * FROM gm WHERE model = 'CORVETTE' AND modelYear = '2022' AND trim = '3LT' AND (exterior_color = 'HYPERSONIC GRAY' OR exterior_color = 'ACCELERATE YELLOW') AND JSON_CONTAINS(allJson->'$.Options', '["ZCR"]');

SELECT * FROM gm
WHERE vin = '1G1YC2D46P5501306';

UPDATE gm SET allJson = '{"maker":"CADILLAC", "model_year":"2022", "mmc_code":"6DD69", "vin":"1G6DG5RKXN0119036", "sitedealer_code":"23027", "sell_source": "12", "order_number": "BDCX99", "creation_date":"4/11/2022", "Options":["AEF", "AEQ", "AF6", "AHC", "AHE", "AHF", "AHH", "AJC", "AJW", "AKE", "AL0", "AM9", "AQ9", "ATH", "AT8", "AVK", "AVN", "AVU", "AXG", "AXJ", "AYG", "A2X", "A45", "A69", "A7K", "BTV", "BYO", "B34", "B35", "B6A", "B70", "CE1", "CF5", "CJ2", "C59", "C73", "DD8", "DEG", "DMB", "D52", "D75", "EF7", "E22", "E28", "FE2", "FJW", "F46", "GJI", "HRD", "HS1", "H2X", "IOT", "JE5", "JF5", "JJ2", "JM8", "J22", "J77", "KA1", "KB7", "KD4", "KI3", "KL9", "KPA", "KRV", "KSG", "KU9", "K12", "K4C", "LAL", "LSY", "MAH", "MCR", "MDB", "M5N", "NB9", "NE1", "NE8", "NK4", "NUG", "N37", "PPW", "PZJ", "Q4D", "RFD", "RSR", "R6M", "R6W", "R9N", "SLM", "TDM", "TFK", "TQ5", "TSQ", "TTW", "T4L", "T8Z", "UC3", "UDD", "UD5", "UEU", "UE1", "UE4", "UFG", "UGE", "UGN", "UG1", "UHX", "UIT", "UJN", "UKC", "UKJ", "UMN", "UQS", "UVB", "UVZ", "U2K", "U2L", "U80", "VHM", "VH9", "VK3", "VRF", "VRG", "VRH", "VRJ", "VRK", "VRL", "VRM", "VRN", "VRR", "VT7", "VV4", "V76", "V8D", "WMW", "XL8", "Y26", "Y5X", "Y5Y", "Y6F", "0ST", "00G", "00Z", "1NF", "1SE", "1SZ", "2NF", "2ST", "4AA", "5A7", "5FC", "6X1", "7X1", "719", "8X2", "9L3", "9X2"]}'
WHERE vin = '1G6DG5RKXN0119036';

UPDATE gm SET trim = 'SPORT', vehicleEngine = '2.0L TURBO, 4-CYL, SIDI', transmission = 'A8', drivetrain = 'AWD', exterior_color = 'SHADOW METALLIC', msrp = '48690', dealer = 'CADILLAC OF MANHATTAN', location = 'NEW YORK, NY 10036-5093', ordernum = 'BDCX99'
WHERE vin = '1G6DG5RKXN0119036';

SELECT * FROM gm WHERE exterior_color = 'PANTHER BLACK MATTE';

SELECT * FROM gm WHERE model = 'CAMARO' AND exterior_color = 'PANTHER BLACK MATTE' ORDER BY SUBSTRING(vin, -6);

SELECT * FROM gm WHERE model = 'CORVETTE Z06';

SELECT JSON_EXTRACT(allJson, '$.mmc_code') AS Options, COUNT(*) as Count
FROM gm
WHERE transmission = 'DCT8'
GROUP BY JSON_EXTRACT(allJson, '$.mmc_code')
ORDER BY Count DESC;

UPDATE gm SET trim = '3LZ'
WHERE model = 'CORVETTE Z06'
AND JSON_CONTAINS(allJson->'$.Options', '["3LZ"]');

SELECT * FROM gm WHERE trim = 'REPLACE';

UPDATE gm
SET allJson = JSON_SET(
    allJson, 
    '$.mmc_code', 
    REPLACE(JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.mmc_code')), ' ', '')
)
WHERE transmission = 'DCT8';

SELECT
    JSON_EXTRACT(allJson, '$.sell_source') AS sell,
    trim AS Trim,
    COUNT(*) AS Count
FROM gm
GROUP BY JSON_EXTRACT(allJson, '$.sell_source'), trim
ORDER BY Count DESC;

SELECT modelYear, model, trim, COUNT(*) AS Count FROM gm GROUP BY modelYear, model, trim;

SELECT modelYear, model, exterior_color, COUNT(*) AS Count FROM gm GROUP BY modelYear, model, exterior_color ORDER BY Count DESC;

SELECT modelYear, model, transmission, COUNT(*) AS Count FROM gm GROUP BY modelYear, model, transmission ORDER BY Count DESC;

SELECT model, vehicleEngine, COUNT(*) AS Count FROM gm GROUP BY model, vehicleEngine ORDER BY Count DESC;

SELECT * FROM gm WHERE JSON_EXTRACT(allJson, '$.sell_source') = "14";

SELECT DISTINCT JSON_EXTRACT(allJson, '$.maker') AS maker
FROM gm
WHERE JSON_EXTRACT(allJson, '$.sell_source') = "12";

SELECT * FROM gm WHERE vin = "1G6D35R67R0810951";

SELECT * FROM gm WHERE modelYear = "2024" AND trim = "V-Series blackwing" AND SUBSTRING(vin, -6)>810920 AND SUBSTRING(vin, -6)<820920;

SELECT * FROM gm WHERE modelYear = "2023" AND model = "CT4" AND trim = "V-SERIES BLACKWING" AND exterior_color = "ELECTRIC BLUE" ORDER BY SUBSTRING(vin, -6);

SELECT * FROM gm WHERE modelYear = "2023" AND model = "CT5" AND trim = "V-SERIES BLACKWING" AND msrp > "118000" AND JSON_CONTAINS(allJson->'$.Options', '["ABQ"]') ORDER BY SUBSTRING(vin, -6);
select * from gm where JSON_CONTAINS(allJson->'$.Options', '["OAR"]');
