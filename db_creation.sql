-- Gym Project DB Creation and Views
-- Group 13: Andrew Pavlak, Aiden Rocha, Vance Elliott, Ethan Devarapalli

-- Create Person Table
-- Note if membership_type already exists delete and dont run create type enum

CREATE TYPE membership_type AS ENUM('monthly', 'yearly', 'instructor', 'admin');

CREATE TABLE IF NOT EXISTS Person(
	userID SERIAL PRIMARY KEY,
	email TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	memType membership_type,
	phone VARCHAR(15) CHECK (phone ~ '^[0-9]{10,15}$'),
	addressID INT REFERENCES Address(addressID),
	loginID INT REFERENCES Login(loginID)
	
);


-- create login table
-- loginID should be serial, and username in particular should be unique for each user, but shared passwords could exist

CREATE TABLE IF NOT EXISTS Login (
	loginID SERIAL PRIMARY KEY,
	Username TEXT NOT NULL UNIQUE,
	Password TEXT NOT NULL
);


-- create address table
-- split address into each of its parts
-- see special note for zip code

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
    adminID INT REFERENCES Person(userID),
    addressID INT REFERENCES Address(addressID)
);

-- Create Class table
-- Note that the times for start and end time are split into 2 columns
-- For now, instructorID references Person.userID, and gymID references Gym.gymID, both as foreign keys

CREATE TABLE IF NOT EXISTS Class(
	classId SERIAL PRIMARY KEY,
	instructorID SERIAL NOT NULL,
	gymID SERIAL NOT NULL,
	className TEXT NOT NULL,
	startTime TIME NOT NULL,
	endTime TIME NOT NULL,
	CHECK (endTime > startTime),
	FOREIGN KEY (instructorID) REFERENCES Person(userID),
    	FOREIGN KEY (gymID) REFERENCES Gym(gymID)
);

-- create enrollmentList table
-- composite primary key between both columns, and both are also foreign keys
-- id references Person.userID, classId references Class.classId

CREATE TABLE IF NOT EXISTS EnrollmentList(
	id SERIAL,
	classId SERIAL,
	PRIMARY KEY (id, classId),
	FOREIGN KEY (id) REFERENCES Person(userID),
	FOREIGN KEY (classId) REFERENCES Class(classId),
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
