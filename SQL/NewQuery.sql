-- Get RPO codes from VIN
SELECT o.option_code
FROM staging_allGM s
JOIN Vehicles v ON s.vin = v.vin
JOIN Options o ON v.vehicle_id = o.vehicle_id
WHERE s.vin = '1G1FH1R78N0102770';

SELECT DISTINCT 
	v.modelYear, 
    v.model, 
    v.body, 
    v.trim, 
    e.engine_type, 
    t.transmission_type, 
    c.color_name, 
    o.country 
FROM vehicles v 
JOIN Engines e ON v.engine_id = e.engine_id 
JOIN Transmissions t ON v.transmission_id = t.transmission_id 
JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
JOIN Colors c ON v.color_id = c.color_id 
JOIN Dealers dl ON v.dealer_id = dl.dealer_id 
JOIN Orders o ON v.order_id = o.order_id;

-- Vehicles.ejs table
SELECT 
    v.vin, 
    v.modelYear, 
    v.model, 
    v.body, 
    v.trim, 
    e.engine_type, 
    t.transmission_type, 
    d.drivetrain_type, 
    c.color_name, 
    v.msrp, 
    o.country, 
    dl.dealer_name
FROM Vehicles v
JOIN Engines e ON v.engine_id = e.engine_id
JOIN Transmissions t ON v.transmission_id = t.transmission_id
JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
JOIN Colors c ON v.color_id = c.color_id
JOIN Orders o ON v.order_id = o.order_id
JOIN Dealers dl ON v.dealer_id = dl.dealer_id;

-- RPO Code Filter
SELECT 
    v.vin, 
    v.modelYear, 
    v.model, 
    v.body, 
    v.trim, 
    e.engine_type, 
    t.transmission_type, 
    d.drivetrain_type, 
    c.color_name, 
    v.msrp, 
    o.country, 
    dl.dealer_name
FROM Vehicles v
JOIN Engines e ON v.engine_id = e.engine_id
JOIN Transmissions t ON v.transmission_id = t.transmission_id
JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
JOIN Colors c ON v.color_id = c.color_id
JOIN Orders o ON v.order_id = o.order_id
JOIN Dealers dl ON v.dealer_id = dl.dealer_id
JOIN Options opt ON v.vehicle_id = opt.vehicle_id
WHERE opt.option_code = 'F55';

-- Search.ejs table
SELECT
    s.vin AS VIN,
    o.creation_date AS Creation_Date,
    s.modelYear AS Year,
    s.model AS Model,
    s.trim AS Trim,
    s.body AS Body,
    e.engine_type AS Engine,
    t.transmission_type AS Transmission,
    dt.drivetrain_type AS Drivetrain,
    c.color_name AS Color,
    s.msrp AS MSRP,
    d.dealer_name AS Dealer,
    d.location AS Location,
    o.country AS Country
FROM staging_allGM s
JOIN Vehicles v ON s.vin = v.vin
JOIN Engines e ON v.engine_id = e.engine_id
JOIN Transmissions t ON v.transmission_id = t.transmission_id
JOIN Drivetrains dt ON v.drivetrain_id = dt.drivetrain_id
JOIN Colors c ON v.color_id = c.color_id
JOIN Dealers d ON v.dealer_id = d.dealer_id
JOIN Orders o ON v.order_id = o.order_id
WHERE s.vin = '1G1F91R68R0107476';



EXPLAIN 
SELECT v.vin, v.modelYear, v.model, v.body, v.trim, 
	e.engine_type, t.transmission_type, d.drivetrain_type, 
	c.color_name, v.msrp, o.country, dl.dealer_name, 
	GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
FROM Vehicles v 
	JOIN Engines e ON v.engine_id = e.engine_id 
	JOIN Transmissions t ON v.transmission_id = t.transmission_id 
	JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
	JOIN Colors c ON v.color_id = c.color_id 
	JOIN Orders o ON v.order_id = o.order_id 
	JOIN Dealers dl ON v.dealer_id = dl.dealer_id 
	LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id 

GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, 
		e.engine_type, t.transmission_type, d.drivetrain_type, 
		c.color_name, v.msrp, o.country, dl.dealer_name

LIMIT 100 OFFSET 0;

explain
        SELECT v.vin, v.modelYear, v.model, v.body, v.trim,
            e.engine_type, t.transmission_type, d.drivetrain_type,
            c.color_name, v.msrp, o.country, dl.dealer_name,
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
        FROM Vehicles v
            JOIN Engines e ON v.engine_id = e.engine_id
            JOIN Transmissions t ON v.transmission_id = t.transmission_id
            JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
            JOIN Colors c ON v.color_id = c.color_id
            JOIN Orders o ON v.order_id = o.order_id
            JOIN Dealers dl ON v.dealer_id = dl.dealer_id
            LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        WHERE trim = 'ZL1'
        GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim,
                e.engine_type, t.transmission_type, d.drivetrain_type,
                c.color_name, v.msrp, o.country, dl.dealer_name

        LIMIT 100 OFFSET 0;
