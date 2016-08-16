CREATE TABLE temperature
(
    timestamp TEXT,
    temperature REAL    --ambient temperature (in degrees Celsius)
);

CREATE TABLE ambient_humidity
(
    timestamp TEXT,
    humidity REAL
);

CREATE TABLE soil_moisture
(
    timestamp TEXT,
    soil_moisture INTEGER
);

CREATE TABLE ambient_light
(
    timestamp TEXT,
    light REAL
);

CREATE TABLE reservoir_level
(
    timestamp TEXT,
    level REAL  -- reservoir level (in mL)
);

CREATE TABLE watering_events
(
    timestamp TEXT,
    water_pumped REAL   --amount of water pumped (in mL)
);