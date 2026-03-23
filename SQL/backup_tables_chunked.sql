-- First, increase system variables for large operations
SET GLOBAL net_read_timeout=600;
SET GLOBAL net_write_timeout=600;
SET GLOBAL max_allowed_packet=268435456;  -- 256MB
SET GLOBAL innodb_buffer_pool_size=4294967296;  -- 4GB
SET GLOBAL innodb_flush_log_at_trx_commit=2;
SET GLOBAL connect_timeout=300;

-- Set session variables
SET SESSION SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET SESSION group_concat_max_len = 1000000;
SET SESSION bulk_insert_buffer_size = 536870912;  -- 512MB

-- Create backup tables
CREATE TABLE IF NOT EXISTS vehicles_backup LIKE Vehicles;
INSERT INTO vehicles_backup SELECT * FROM Vehicles;

-- Break down Options backup into smaller chunks
CREATE TABLE IF NOT EXISTS options_backup LIKE Options;

-- First, let's get the min and max vehicle_id to determine our range
SELECT MIN(vehicle_id) as min_id, MAX(vehicle_id) as max_id FROM Options;

-- Then insert in chunks of 100,000 records
DELIMITER //
CREATE PROCEDURE backup_options_in_chunks()
BEGIN
    DECLARE start_id BIGINT;
    DECLARE end_id BIGINT;
    DECLARE chunk_size INT DEFAULT 100000;
    
    SELECT MIN(vehicle_id), MAX(vehicle_id) 
    INTO start_id, end_id 
    FROM Options;
    
    WHILE start_id <= end_id DO
        INSERT INTO options_backup 
        SELECT * FROM Options 
        WHERE vehicle_id BETWEEN start_id AND start_id + chunk_size - 1;
        
        SET start_id = start_id + chunk_size;
        
        -- Add a small delay between chunks
        DO SLEEP(1);
    END WHILE;
END //
DELIMITER ;

-- Execute the backup procedure
CALL backup_options_in_chunks();

-- Drop the procedure after use
DROP PROCEDURE IF EXISTS backup_options_in_chunks;

-- Verify the backup
SELECT COUNT(*) as original_count FROM Options;
SELECT COUNT(*) as backup_count FROM options_backup;