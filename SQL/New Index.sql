CREATE INDEX idx_vehicle_full_query 
ON Vehicles (
    modelYear,      -- Often filtered/grouped
    model,          -- Often filtered/grouped
    body,           -- Often filtered/grouped
    trim,           -- Often filtered/grouped
    engine_id,      -- Foreign Key
    transmission_id,-- Foreign Key
    drivetrain_id,  -- Foreign Key
    color_id,       -- Foreign Key
    order_id,       -- Foreign Key
    dealer_id,      -- Foreign Key (used in /search)
    msrp,           -- Used for sorting
    vin             -- Used for identification (in the final result)
);
