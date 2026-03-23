SELECT 
    TABLE_NAME, 
    COLUMN_NAME, 
    INDEX_NAME, 
    NON_UNIQUE, 
    SEQ_IN_INDEX, 
    CARDINALITY
FROM 
    information_schema.statistics
WHERE 
    TABLE_SCHEMA = 'vehicles'
ORDER BY 
    TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
    
-- Remove the smaller specialist indexes
DROP INDEX idx_veh_core_filters ON Vehicles;
DROP INDEX idx_veh_mechanical ON Vehicles;
DROP INDEX idx_veh_msrp ON Vehicles;

-- CREATE THE SUPER-COVERING INDEX
-- Column order is critical here: Filtered columns first, Joined columns second, Sorted columns last.
CREATE INDEX idx_veh_search_covering ON Vehicles (
    modelYear,      -- Filter 1
    model,          -- Filter 2
    body,           -- Filter 3
    trim,           -- Filter 4
    engine_id,      -- Join 1
    transmission_id,-- Join 2
    color_id,       -- Join 3
    drivetrain_id,  -- Join 4
    order_id,       -- Join 5
    msrp,           -- Sorting
    vin             -- SELECT result
);

DROP INDEX idx_orders_country ON Orders;

CREATE INDEX idx_orders_covering ON Orders (
    country, 
    order_id, 
    creation_date, 
    order_number
);

-- Fast lookup for Special Editions (Special desc is now included in the index)
DROP INDEX idx_specialeditions_vehicle ON SpecialEditions;
CREATE INDEX idx_se_covering ON SpecialEditions (vehicle_id, special_desc);

-- Fast lookup for RPOs (This is your most scanned join)
DROP INDEX idx_options_v_code ON Options;
CREATE INDEX idx_options_covering ON Options (vehicle_id, option_code);

ANALYZE TABLE Vehicles, Options, Orders, SpecialEditions;
    