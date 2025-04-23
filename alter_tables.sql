-- -- Drop the existing foreign key constraint on addressID
-- ALTER TABLE Person
-- DROP CONSTRAINT person_addressid_fkey;

-- -- Re-add the foreign key constraint with ON DELETE CASCADE for addressID
-- ALTER TABLE Person
-- ADD CONSTRAINT person_addressid_fkey
-- FOREIGN KEY (addressID)
-- REFERENCES Address(addressID)
-- ON DELETE CASCADE;

-- -- Drop the existing foreign key constraint on loginID
-- ALTER TABLE Person
-- DROP CONSTRAINT person_loginid_fkey;

-- -- Re-add the foreign key constraint with ON DELETE CASCADE for loginID
-- ALTER TABLE Person
-- ADD CONSTRAINT person_loginid_fkey
-- FOREIGN KEY (loginID)
-- REFERENCES Login(loginID)
-- ON DELETE CASCADE;

-- -- Drop existing constraints if unnamed (replace with actual constraint names if needed)
-- ALTER TABLE Gym DROP CONSTRAINT IF EXISTS gym_adminid_fkey;
-- ALTER TABLE Gym DROP CONSTRAINT IF EXISTS gym_addressid_fkey;

-- -- Add cascading foreign key constraints
-- ALTER TABLE Gym
-- ADD CONSTRAINT gym_adminid_fkey
-- FOREIGN KEY (adminID)
-- REFERENCES Person(userID)
-- ON DELETE CASCADE;

-- ALTER TABLE Gym
-- ADD CONSTRAINT gym_addressid_fkey
-- FOREIGN KEY (addressID)
-- REFERENCES Address(addressID)
-- ON DELETE CASCADE;

-- ALTER TABLE Class DROP CONSTRAINT IF EXISTS class_instructorid_fkey;
-- ALTER TABLE Class DROP CONSTRAINT IF EXISTS class_gymid_fkey;

-- ALTER TABLE Class
-- ADD CONSTRAINT class_instructorid_fkey
-- FOREIGN KEY (instructorID)
-- REFERENCES Person(userID)
-- ON DELETE CASCADE;

-- ALTER TABLE Class
-- ADD CONSTRAINT class_gymid_fkey
-- FOREIGN KEY (gymID)
-- REFERENCES Gym(gymID)
-- ON DELETE CASCADE;

-- -- Step 1: Drop the existing foreign key constraint
-- ALTER TABLE enrollmentlist
-- DROP CONSTRAINT IF EXISTS enrollmentlist_id_fkey;

-- -- Step 2: Add the constraint back with ON DELETE CASCADE
-- ALTER TABLE enrollmentlist
-- ADD CONSTRAINT enrollmentlist_id_fkey
-- FOREIGN KEY (id)
-- REFERENCES public.person (userid)
-- ON DELETE CASCADE;

-- ALTER TABLE public.enrollmentlist
-- DROP CONSTRAINT enrollmentlist_classid_fkey;

-- ALTER TABLE public.enrollmentlist
-- ADD CONSTRAINT enrollmentlist_classid_fkey
-- FOREIGN KEY (classid)
-- REFERENCES public.class (classid)
-- ON UPDATE NO ACTION
-- ON DELETE CASCADE;


-- -- Step 1: Drop the existing foreign key constraint
-- ALTER TABLE public.facilities
-- DROP CONSTRAINT IF EXISTS facilities_gymid_fkey;

-- -- Step 2: Add the constraint back with ON DELETE CASCADE
-- ALTER TABLE public.facilities
-- ADD CONSTRAINT facilities_gymid_fkey
-- FOREIGN KEY (gymid)
-- REFERENCES public.gym (gymid)
-- ON DELETE CASCADE;

-- Step 1: Drop the current foreign key constraints
ALTER TABLE public.gymenrollment
DROP CONSTRAINT IF EXISTS fk_gym;

ALTER TABLE public.gymenrollment
DROP CONSTRAINT IF EXISTS fk_person_member;

-- Step 2: Add the constraints back with ON DELETE CASCADE
ALTER TABLE public.gymenrollment
ADD CONSTRAINT fk_gym
FOREIGN KEY (gymid)
REFERENCES public.gym (gymid)
ON DELETE CASCADE;

ALTER TABLE public.gymenrollment
ADD CONSTRAINT fk_person_member
FOREIGN KEY (userid)
REFERENCES public.person (userid)
ON DELETE CASCADE;



