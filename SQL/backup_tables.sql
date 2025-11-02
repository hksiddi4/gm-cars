-- First, increase the timeout and max allowed packet size
SET GLOBAL net_read_timeout=300;
SET GLOBAL net_write_timeout=300;
SET GLOBAL max_allowed_packet=67108864;

-- Create backup tables
CREATE TABLE IF NOT EXISTS vehicles_backup LIKE Vehicles;
INSERT INTO vehicles_backup SELECT * FROM Vehicles;

-- Break down Options backup into chunks
CREATE TABLE IF NOT EXISTS options_backup LIKE Options;
INSERT INTO options_backup 
SELECT * FROM Options 
ORDER BY vehicle_id 
LIMIT 1000000;  -- Adjust this number based on your table size

-- You can repeat the above INSERT with OFFSET if needed:
-- INSERT INTO options_backup 
-- SELECT * FROM Options 
-- ORDER BY vehicle_id 
-- LIMIT 1000000 OFFSET 1000000;