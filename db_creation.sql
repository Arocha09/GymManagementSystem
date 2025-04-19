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

-- ALTER TABLE Person
--  ADD CONSTRAINT uq_person_usermem UNIQUE(userID, memType);
-- code to alter table to force unique constraint on both userID & memType which are linked



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


-- create the gymEnrollment table, which links members with gyms
-- note that id is the new primary key of this table, which is just a serial that links userID and gymID
-- otherwise, userID is from Person.userID, and introduce a constraint that makes sure it's only members being filtered here
-- gymID is from Gym.gymID

CREATE TABLE IF NOT EXISTS GymEnrollment(
    id SERIAL PRIMARY KEY,
    userID INT NOT NULL,
    gymID INT NOT NULL,
    memType membership_type NOT NULL,

    CONSTRAINT chk_memtype CHECK (memType IN ('monthly','yearly')),
    CONSTRAINT fk_person_member
        FOREIGN KEY (userID, memType) REFERENCES Person(userID, memType),
    CONSTRAINT fk_gym
        FOREIGN KEY (gymID) REFERENCES Gym(gymID)
);

-- Insert data into Login table
INSERT INTO Login (Username, Password) 
VALUES
    ('john_doe', 'password123'),
    ('jane_doe', 'password456'),
    ('admin_user', 'adminpassword');

-- Insert data into Address table
INSERT INTO Address (StName, City, State, Zip)
VALUES
    ('123 Elm St', 'Springfield', 'IL', '62701'),
    ('456 Oak St', 'Champaign', 'IL', '61820'),
    ('789 Pine St', 'Chicago', 'IL', '60616');

-- Insert data into Person table
INSERT INTO Person (email, name, memType, phone, addressID, loginID)
VALUES
    ('john.doe@example.com', 'John Doe', 'monthly', '5551234567', 1, 1),
    ('jane.doe@example.com', 'Jane Doe', 'yearly', '5552345678', 2, 2),
    ('admin@example.com', 'Admin User', 'admin', '5553456789', 3, 3);

-- Insert data into Gym table
INSERT INTO Gym (gymName, gymOpen, gymClose, adminID, addressID)
VALUES
    ('Fitness World', '06:00:00', '22:00:00', 3, 1),
    ('Powerhouse Gym', '05:00:00', '23:00:00', 3, 2),
    ('Health Club', '07:00:00', '21:00:00', 3, 3);

-- Insert data into Class table
INSERT INTO Class (instructorID, gymID, className, startTime, endTime)
VALUES
    (1, 1, 'Yoga', '07:00:00', '08:00:00'),
    (2, 2, 'Spin Class', '08:00:00', '09:00:00'),
    (3, 3, 'Zumba', '09:00:00', '10:00:00');

-- Insert data into EnrollmentList table
INSERT INTO EnrollmentList (id, classId)
VALUES
    (1, 1),
    (2, 2),
    (3, 3);

-- Insert data into Facilities table
INSERT INTO Facilities (facilityName, facilityOpen, facilityClose, gymID)
VALUES
    ('Pool', '06:00:00', '22:00:00', 1),
    ('Sauna', '07:00:00', '20:00:00', 2),
    ('Tennis Court', '08:00:00', '21:00:00', 3);


-- Creates a view where a user can see each class they're enrolled in, and what times.
CREATE VIEW MemberClasses AS 
SELECT className, startTime, endTime 
FROM ((Person a JOIN EnrollmentList b ON a.userID = b.id ) c
JOIN Class d ON c.classId = d.classId)
WHERE userID = '1';


-- Creates a view where admin can see how many people are enrolled in each class
CREATE VIEW numEnrolls AS 
SELECT a.classId, count(ID)
FROM (EnrollmentList a JOIN Class b ON a.classId = b.classId)
GROUP BY a.classId;