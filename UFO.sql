CREATE DATABASE area52;
USE area52;

-- Criar a coluna `location_id`
ALTER TABLE area52 ADD COLUMN location_id INT;

-- Atribuir IDs únicos a localizações com base em latitude e longitude
UPDATE area52 a
JOIN (
    SELECT latitude, longitude, 
           ROW_NUMBER() OVER (ORDER BY latitude, longitude) AS location_id
    FROM (SELECT DISTINCT latitude, longitude FROM area52) AS unique_locations
) temp ON a.latitude = temp.latitude AND a.longitude = temp.longitude
SET a.location_id = temp.location_id;

-- Criar a coluna `shape_id`
ALTER TABLE area52 ADD COLUMN shape_id INT;

-- Garantir IDs únicos para shapes
UPDATE area52 a
JOIN (
    SELECT shape, 
           ROW_NUMBER() OVER (ORDER BY shape) AS shape_id
    FROM (SELECT DISTINCT shape FROM area52) AS unique_shapes
) temp ON a.shape = temp.shape
SET a.shape_id = temp.shape_id;

-- Criar a coluna `duration_id`
ALTER TABLE area52 ADD COLUMN duration_id INT;

-- Atribuir IDs únicos a durations com base em `durationseconds`
UPDATE area52 a
JOIN (
    SELECT durationseconds, 
           ROW_NUMBER() OVER (ORDER BY durationseconds) AS duration_id
    FROM (SELECT DISTINCT durationseconds FROM area52) AS unique_durations
) temp ON a.durationseconds = temp.durationseconds
SET a.duration_id = temp.duration_id;

-- Criar a tabela `locations`
CREATE TABLE locations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    UNIQUE(latitude, longitude)  -- Evita duplicação
);

INSERT INTO locations (latitude, longitude)
SELECT DISTINCT latitude, longitude FROM area52;

-- Criar a tabela `shapes`
CREATE TABLE shapes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    shape_name TEXT NOT NULL,
    UNIQUE(shape_name)  -- Evita duplicação
);

-- correção da tabela shapes
ALTER TABLE shapes DROP INDEX shape_name;
ALTER TABLE shapes MODIFY shape_name VARCHAR(255);
ALTER TABLE shapes ADD UNIQUE (shape_name);

-- inserir dados na tabela shapes
INSERT INTO shapes (shape_name)
SELECT DISTINCT shape FROM area52;

-- Criar a tabela `durations`
CREATE TABLE durations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    durationseconds INT NOT NULL,
    UNIQUE(durationseconds)  -- Evita duplicação
);

INSERT INTO durations (durationseconds)
SELECT DISTINCT durationseconds FROM area52;

-- Criar a tabela `sightings`
CREATE TABLE sightings (
    id_sighting INT PRIMARY KEY AUTO_INCREMENT,
    datetime_sighting TEXT NOT NULL,
    location_id INT NOT NULL,
    shape_id INT NOT NULL,
    duration_id INT NOT NULL,
    comments TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (shape_id) REFERENCES shapes(id),
    FOREIGN KEY (duration_id) REFERENCES durations(id)
);

-- Transferir os dados para a `sightings`
INSERT INTO sightings (id_sighting, datetime_sighting, location_id, shape_id, duration_id, comments)
SELECT id_sighting, datetime_sighting, location_id, shape_id, duration_id, comments FROM area52;

-- Verificar se todos os IDs foram preenchidos corretamente
SELECT COUNT(*) FROM sightings WHERE location_id IS NULL OR shape_id IS NULL OR duration_id IS NULL;

-- Remover a tabela original `area52` após a migração
DROP TABLE area52;