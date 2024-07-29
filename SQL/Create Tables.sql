CREATE DATABASE vehicles;
USE vehicles;

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

SELECT * FROM gm LIMIT 50;
