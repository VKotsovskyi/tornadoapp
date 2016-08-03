SET SESSION time_zone = "+0:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS lists;
CREATE TABLE lists (
    id SERIAL,
    title VARCHAR(512) NOT NULL,
    description TEXT NOT NULL,
    published TIMESTAMP NOT NULL,
    updated TIMESTAMP NOT NULL
);

