-- Hashed passsword is: $2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu
PRAGMA foreign_keys = ON; -- Enable foreign key support

DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_pk                 TEXT,
    user_username           TEXT,
    user_name               TEXT,
    user_last_name          TEXT,
    user_email              TEXT UNIQUE,
    user_password           TEXT,
    user_role               TEXT,
    user_created_at         INTEGER,
    user_updated_at         INTEGER,
    user_is_verified        INTEGER,
    user_is_blocked         INTEGER,
    user_is_deleted         INTEGER
    PRIMARY KEY(user_pk)
) WITHOUT ROWID;

INSERT INTO users VALUES(
    "d11854217ecc42b2bb17367fe33dc8f4",
    "thildolas",
    "Mathilde",
    "Laursen",
    "admin@company.com",
    "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
    "admin",
    1712674758,
    0,
    1,
    0
);

ALTER TABLE users ADD COLUMN user_deleted_at INTEGER DEFAULT 0;

SELECT * FROM users;


DROP TABLE IF EXISTS properties;

CREATE TABLE properties(
    property_pk                 TEXT,
    property_name               TEXT,
    property_splash_image       TEXT,
    property_lat                TEXT,
    property_lon                TEXT,
    property_stars              REAL,
    property_price_per_night    REAL,
    property_created_at         INTEGER,
    property_updated_at         INTEGER,
    PRIMARY KEY(property_pk)
) WITHOUT ROWID;

INSERT INTO properties VALUES
("7e862e9b-d4bb-4f91-8686-b29f2b53e539", "Tranquil Retreat", "house_image_1.webp",55.6761123,12.5370567, 5, 2541, 1, 0),
("58c9ab83-11e9-42b3-b31a-2a709d231dd6", "Cozy Cottage", "house_image_2.webp",  55.7117212, 12.3795250, 4.97, 985, 2, 0),
("bcd7ec60-293b-428d-9ab2-bdcd3231c8e8", "Sunnybrook Bungalow", "house_image_3.webp", 55.6994, 12.5918, 3.45, 429, 3, 0),
("70a43129-17ce-4943-b376-cc4149c51a2c", "Serene Meadow Cabin", "house_image_4.webp", 55.836659, 12.472993, 4, 655, 4, 0),
("d5bd1e8b-bc61-40d5-85bd-d7f8f36bc7ce", "Harmony Hill Haven", "house_image_5.webp", 55.6846, 12.58709, 3.5, 1200, 5, 0),
("da78803f-cf0c-46fa-a87a-36582ddc87e0", "Copenhagen Cool Poolhouse", "house_image_6.webp",  55.67588478896283,12.44691320387957, 4.57, 1975, 6, 0),
("9ad72bd1-fe73-41fc-8e47-2d84e5bc590e", "Enchanted Forest Cottage", "house_image_7.webp", 55.6867, 12.5734, 5, 600, 7, 0),
("23eb005d-6a52-49e8-83b6-0c43cdf6d03b", "Sleek sunny House", "house_image_8.webp", 55.6772, 12.5784, 4.80, 2100, 8, 0),
("3bd04a85-99e8-41fc-89e7-b893628b616d", "Sunny Birch Cabin", "house_image_9.webp", 55.73524858655415, 12.423186638255095, 4.7, 685, 9, 0),
("54e9625b-9d06-417f-939b-f0ea32c036e7", "Urban Zen Retreat", "house_image_10.webp", 55.73898609501771, 12.576515434384987, 3.2, 385,10, 0),
("3a777ca4-d837-4376-a074-9eff6a0436cb",  "Comfort Villa", "house_image_11.webp", 55.748299111459716, 12.498336277346084, 3.8, 585, 11, 0),
("36d55a3f-c81e-4770-9740-02199b31037c", "Modern Minimalist Haven", "house_image_12.webp", 55.67973421890946, 12.538855840492772, 4.5, 2600,12, 0);

-- (page_number - 1) * ITEMS_PER_PAGE
-- (1 - 1) * 3 = 10 1 2
-- (2 - 1) * 3 = 3 4 5
-- (3 - 1) * 3 = 6 7 8


-- Page 4
-- 0 3 6 9
SELECT * FROM properties 
ORDER BY property_created_at
LIMIT 9,3;


-- offset = (currentPage - 1) * propertiesPerPage
-- page 1 = 1 2 3+
-- page 2 = 4 5 6
-- page 3 = 7 8 9
-- page 4 = 10
SELECT * FROM properties 
ORDER BY property_created_at
LIMIT 3 OFFSET 9;



DROP TABLE if EXISTS bookings;

CREATE TABLE bookings (
    user_fk             TEXT,
    property_fk   TEXT,
    PRIMARY KEY (user_fk, property_fk),
    FOREIGN KEY(user_fk) REFERENCES users(user_pk)
    FOREIGN KEY(property_fk) REFERENCES properties(property_pk)
) WITHOUT ROWID;


INSERT INTO bookings VALUES ("42be17c8273e4de5b9d3c3303e65a6ca","9ad72bd1-fe73-41fc-8e47-2d84e5bc590e")
SELECT * FROM bookings




DROP TABLE if EXISTS partners_properties;

CREATE TABLE partners_properties (
    user_fk             TEXT,
    property_fk   TEXT,
    PRIMARY KEY (user_fk, property_fk),
    FOREIGN KEY(user_fk) REFERENCES users(user_pk)
    FOREIGN KEY(property_fk) REFERENCES properties(property_pk)
) WITHOUT ROWID;


INSERT INTO partners_properties VALUES 
("42be17c8273e4de5b9d3c3303e65a6ca","7e862e9b-d4bb-4f91-8686-b29f2b53e539"),
("42be17c8273e4de5b9d3c3303e65a6ca","58c9ab83-11e9-42b3-b31a-2a709d231dd6"),
("42be17c8273e4de5b9d3c3303e65a6ca","bcd7ec60-293b-428d-9ab2-bdcd3231c8e8"),
("3083ea294e394c1ab03e26c476e367db","70a43129-17ce-4943-b376-cc4149c51a2c"),
("3083ea294e394c1ab03e26c476e367db","d5bd1e8b-bc61-40d5-85bd-d7f8f36bc7ce"),
("0ee77f976aa64f61a977da5e754210c0","da78803f-cf0c-46fa-a87a-36582ddc87e0"),
("0ee77f976aa64f61a977da5e754210c0","9ad72bd1-fe73-41fc-8e47-2d84e5bc590e");
SELECT * FROM partners_properties;


DROP TABLE if EXISTS user_verification;

CREATE TABLE user_verification (
    user_fk             TEXT,
    verification_code   TEXT,
    PRIMARY KEY (user_fk, verification_code),
    FOREIGN KEY(user_fk) REFERENCES users(user_pk)
) WITHOUT ROWID;





DROP TABLE IF EXISTS password_reset;

CREATE TABLE password_reset (
    user_fk TEXT,
    reset_token TEXT,
    expiration_time TIMESTAMP,
    PRIMARY KEY (user_fk),
    FOREIGN KEY (user_fk) REFERENCES users(user_pk)
) WITHOUT ROWID;















