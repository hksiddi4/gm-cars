SELECT * FROM gm
WHERE vin = '1G1FK1R63N0133210';

CREATE TABLE IF NOT EXISTS rpo (
	rpo varchar(3),
    feature varchar(255)
);

SELECT * FROM rpo
WHERE feature ='Base Equipment Package'
ORDER BY rpo;

INSERT INTO rpo VALUES ('1SS', 'Base Equipment Package');

SELECT * FROM gm ORDER BY RAND() LIMIT 25;

-- Find duplicate options
SELECT JSON_EXTRACT(allJson, '$.Options') AS Options, COUNT(*) as Count
FROM gm
GROUP BY JSON_EXTRACT(allJson, '$.Options')
HAVING COUNT(*) > 1
ORDER BY Count DESC;
