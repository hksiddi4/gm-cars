-- Backup tables (optional, but recommended)
CREATE TABLE IF NOT EXISTS vehicles_backup AS SELECT * FROM Vehicles;
CREATE TABLE IF NOT EXISTS options_backup AS SELECT * FROM Options;

-- Add indexes to existing tables
ALTER TABLE Vehicles ADD INDEX idx_vehicle_model_year (model, modelYear);
ALTER TABLE Vehicles ADD INDEX idx_vehicle_body_trim (body, trim);
ALTER TABLE Vehicles ADD INDEX idx_vehicle_engine (engine_id);
ALTER TABLE Vehicles ADD INDEX idx_vehicle_transmission (transmission_id);
ALTER TABLE Vehicles ADD INDEX idx_vehicle_color (color_id);
ALTER TABLE Vehicles ADD INDEX idx_vehicle_msrp (msrp);

-- Create RPO tables for better RPO searching
CREATE TABLE IF NOT EXISTS RPO_Codes (
    rpo_id SERIAL PRIMARY KEY,
    rpo_code VARCHAR(3),
    description VARCHAR(255),
    category VARCHAR(50),
    INDEX idx_rpo_code (rpo_code)
);

-- Create vehicle_rpo junction table
CREATE TABLE IF NOT EXISTS Vehicle_RPO (
    vehicle_id BIGINT,
    rpo_id BIGINT,
    PRIMARY KEY (vehicle_id, rpo_id),
    INDEX idx_rpo_vehicle (rpo_id, vehicle_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (rpo_id) REFERENCES RPO_Codes(rpo_id) ON DELETE CASCADE
);

-- Add indexes to other tables
ALTER TABLE Orders ADD INDEX idx_order_date (creation_date);
ALTER TABLE Orders ADD INDEX idx_order_country (country);
ALTER TABLE Colors ADD INDEX idx_color_name (color_name);

-- Create materialized view for RPO searches
CREATE TABLE vehicle_rpo_mv (
    vehicle_id BIGINT,
    vin VARCHAR(17),
    rpo_codes TEXT,
    PRIMARY KEY (vehicle_id),
    INDEX idx_rpo_search (rpo_codes(255))
) AS
SELECT 
    v.vehicle_id,
    v.vin,
    GROUP_CONCAT(DISTINCT opt.option_code ORDER BY opt.option_code) as rpo_codes
FROM Vehicles v
LEFT JOIN Options opt ON v.vehicle_id = opt.vehicle_id
GROUP BY v.vehicle_id, v.vin;

-- Create refresh procedure for the materialized view
DELIMITER //
CREATE PROCEDURE refresh_rpo_mv()
BEGIN
    TRUNCATE TABLE vehicle_rpo_mv;
    INSERT INTO vehicle_rpo_mv
    SELECT 
        v.vehicle_id,
        v.vin,
        GROUP_CONCAT(DISTINCT opt.option_code ORDER BY opt.option_code) as rpo_codes
    FROM Vehicles v
    LEFT JOIN Options opt ON v.vehicle_id = opt.vehicle_id
    GROUP BY v.vehicle_id, v.vin;
END //
DELIMITER ;

-- Create a trigger to keep the materialized view updated
DELIMITER //
CREATE TRIGGER update_rpo_mv_after_insert
AFTER INSERT ON Options
FOR EACH ROW
BEGIN
    CALL refresh_rpo_mv();
END //

CREATE TRIGGER update_rpo_mv_after_delete
AFTER DELETE ON Options
FOR EACH ROW
BEGIN
    CALL refresh_rpo_mv();
END //
DELIMITER ;

-- Create stored procedures for common queries
DELIMITER //
CREATE PROCEDURE get_vehicle_details(IN p_vin VARCHAR(17))
BEGIN
    SELECT v.vin, v.modelYear, v.model, v.body, v.trim, 
           e.engine_type, t.transmission_type, d.drivetrain_type, 
           c.color_name, v.msrp, o.country, o.order_number,
           mc.mmc_code, o.creation_date, dl.dealer_name, 
           dl.location, GROUP_CONCAT(DISTINCT se.special_desc) as special_desc,
           GROUP_CONCAT(DISTINCT opt.option_code) as rpo_codes
    FROM Vehicles v
        USE INDEX (idx_vehicle_model_year)
        JOIN Engines e ON v.engine_id = e.engine_id 
        JOIN Transmissions t ON v.transmission_id = t.transmission_id 
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
        JOIN Colors c ON v.color_id = c.color_id 
        JOIN Orders o ON v.order_id = o.order_id 
        JOIN Dealers dl ON v.dealer_id = dl.dealer_id
        LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        LEFT JOIN Options opt ON v.vehicle_id = opt.vehicle_id
        LEFT JOIN MMC_Codes mc ON o.mmc_code_id = mc.mmc_code_id
    WHERE v.vin = p_vin
    GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, 
             e.engine_type, t.transmission_type, d.drivetrain_type, 
             c.color_name, v.msrp, o.country, o.order_number,
             mc.mmc_code, o.creation_date, dl.dealer_name, dl.location;
END //

CREATE PROCEDURE get_vehicles_filtered(
    IN p_year VARCHAR(4),
    IN p_body VARCHAR(32),
    IN p_trim VARCHAR(32),
    IN p_engine VARCHAR(48),
    IN p_trans VARCHAR(4),
    IN p_model VARCHAR(32),
    IN p_color VARCHAR(64),
    IN p_country VARCHAR(8),
    IN p_rpo VARCHAR(1000),
    IN p_order VARCHAR(10),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SET @sql = CONCAT('
        SELECT SQL_CALC_FOUND_ROWS 
            v.vin, v.modelYear, v.model, v.body, v.trim, 
            e.engine_type, t.transmission_type, d.drivetrain_type, 
            c.color_name, v.msrp, o.country, 
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ", ") AS special_desc
        FROM Vehicles v
            USE INDEX (idx_vehicle_model_year, idx_vehicle_body_trim)
            JOIN Engines e ON v.engine_id = e.engine_id 
            JOIN Transmissions t ON v.transmission_id = t.transmission_id 
            JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
            JOIN Colors c ON v.color_id = c.color_id 
            JOIN Orders o ON v.order_id = o.order_id
            LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
            LEFT JOIN vehicle_rpo_mv vrm ON v.vehicle_id = vrm.vehicle_id
        WHERE 1=1 ',
        IF(p_year IS NOT NULL, ' AND v.modelYear = ?', ''),
        IF(p_body IS NOT NULL, ' AND v.body = ?', ''),
        IF(p_trim IS NOT NULL, ' AND v.trim = ?', ''),
        IF(p_engine IS NOT NULL, ' AND e.engine_type = ?', ''),
        IF(p_trans IS NOT NULL, ' AND t.transmission_type = ?', ''),
        IF(p_model IS NOT NULL, ' AND v.model = ?', ''),
        IF(p_color IS NOT NULL, ' AND c.color_name = ?', ''),
        IF(p_country IS NOT NULL, ' AND o.country = ?', ''),
        IF(p_rpo IS NOT NULL, ' AND FIND_IN_SET(?, vrm.rpo_codes)', ''),
        ' GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, 
            e.engine_type, t.transmission_type, d.drivetrain_type, 
            c.color_name, v.msrp, o.country ',
        CASE p_order
            WHEN 'ASC' THEN ' ORDER BY v.msrp ASC'
            WHEN 'DESC' THEN ' ORDER BY v.msrp DESC'
            WHEN 'vinASC' THEN ' ORDER BY v.vin ASC'
            WHEN 'vinDESC' THEN ' ORDER BY v.vin DESC'
            ELSE ' ORDER BY v.msrp DESC'
        END,
        ' LIMIT ? OFFSET ?'
    );

    SET @params = '';
    SET @values = JSON_ARRAY();

    IF p_year IS NOT NULL THEN
        SET @params = CONCAT(@params, 's');
        SET @values = JSON_ARRAY_APPEND(@values, '$', p_year);
    END IF;
    -- Add similar blocks for other parameters

    PREPARE stmt FROM @sql;
    EXECUTE stmt USING @values;
    DEALLOCATE PREPARE stmt;

    -- Get total count
    SELECT FOUND_ROWS() as total;
END //
DELIMITER ;

-- Optimize database configuration
SET GLOBAL innodb_buffer_pool_size = 4294967296;  -- 4GB
SET GLOBAL innodb_log_file_size = 268435456;      -- 256MB
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL innodb_file_per_table = 1;
SET GLOBAL query_cache_type = 0;
SET GLOBAL query_cache_size = 0;