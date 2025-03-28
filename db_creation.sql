-- sample commit by Ethan (comment)


-- create login table

CREATE TABLE IF NOT EXISTS Login (
	loginID SERIAL PRIMARY KEY,
	Username TEXT NOT NULL UNIQUE,
	Password TEXT NOT NULL
);


-- create address table

CREATE TABLE IF NOT EXISTS Address (
	addressID SERIAL PRIMARY KEY,
	StName TEXT NOT NULL,
	City TEXT NOT NULL,
	State TEXT NOT NULL,
	Zip CHAR(5) NOT NULL CHECK (Zip ~ '^[0-9]{5}$') -- note that I made zip code a chr variable with exactly 5 digits only, which is why the regex is in there
);


-- Create Gym table
-- Note time columns for open and close not a single column

CREATE TABLE IF NOT EXISTS Gym (
    gymID SERIAL PRIMARY KEY,
    gymName TEXT NOT NULL,
    gymOpen TIME NOT NULL,
    gymClose TIME NOT NULL,
    adminID INT REFERENCES Person(personID),
    addressID INT REFERENCES Address(addressID)
);


-- Create Facilities Table
-- Note time columns for open and close not a single column

CREATE TABLE IF NOT EXISTS Facilities(
    facilityID SERIAL PRIMARY KEY,
    facilityName TEXT NOT NULL,
    facilityOpen TIME NOT NULL,
    facilityClose TIME NOT NULL,
    gymID INT REFERENCES Gym(gymID)
);