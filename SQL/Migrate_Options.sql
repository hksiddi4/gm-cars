-- Step 1: Ensure Options_New exists with the optimal schema
CREATE TABLE IF NOT EXISTS `Options_New` (
  `vehicle_id` BIGINT UNSIGNED NOT NULL,
  `option_code` CHAR(3) NOT NULL,
  PRIMARY KEY (`vehicle_id`, `option_code`),
  CONSTRAINT `fk_options_vehicle_id`
    FOREIGN KEY (`vehicle_id`) REFERENCES `Vehicles` (`vehicle_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 2: Migrate all data from the current Options table into Options_New.
-- We use INSERT IGNORE so that if Options_New already has some of the rows,
-- they won't cause duplicate key errors.
INSERT IGNORE INTO `Options_New` (`vehicle_id`, `option_code`)
SELECT `vehicle_id`, `option_code` FROM `Options`;

-- Step 3: Swap the tables!
-- We rename the old one to Options_Old, and the new optimized one to Options.
RENAME TABLE `Options` TO `Options_Old`, `Options_New` TO `Options`;

-- At this point, Options is now the optimized table containing all data from both!
-- Once you verify everything is working, you can optionally drop Options_Old:
-- DROP TABLE `Options_Old`;
