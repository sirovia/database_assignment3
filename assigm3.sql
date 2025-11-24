-- USERS table
CREATE TABLE USERS (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    profile_description TEXT,
    password VARCHAR(255) NOT NULL
);

-- CAREGIVER table
CREATE TABLE CAREGIVER (
    caregiver_user_id INT PRIMARY KEY REFERENCES USERS(user_id) ON DELETE CASCADE,
    photo TEXT,
    gender VARCHAR(10),
    caregiving_type VARCHAR(50) CHECK (caregiving_type IN ('babysitter', 'caregiver for elderly', 'playmate for children')),
    hourly_rate NUMERIC(10,2) NOT NULL
);

-- MEMBER table
CREATE TABLE MEMBER (
    member_user_id INT PRIMARY KEY REFERENCES USERS(user_id) ON DELETE CASCADE,
    house_rules TEXT,
    dependent_description TEXT
);

-- ADDRESS table
CREATE TABLE ADDRESS (
    member_user_id INT PRIMARY KEY REFERENCES MEMBER(member_user_id) ON DELETE CASCADE,
    house_number VARCHAR(20) NOT NULL,
    street VARCHAR(255) NOT NULL,
    town VARCHAR(100) NOT NULL
);

-- JOB table
CREATE TABLE JOB (
    job_id SERIAL PRIMARY KEY,
    member_user_id INT NOT NULL REFERENCES MEMBER(member_user_id) ON DELETE CASCADE,
    required_caregiving_type VARCHAR(50) CHECK (required_caregiving_type IN ('babysitter', 'caregiver for elderly', 'playmate for children')),
    other_requirements TEXT,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- JOB_APPLICATION table
CREATE TABLE JOB_APPLICATION (
    caregiver_user_id INT NOT NULL REFERENCES CAREGIVER(caregiver_user_id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES JOB(job_id) ON DELETE CASCADE,
    date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (caregiver_user_id, job_id)
);

-- APPOINTMENT table
CREATE TABLE APPOINTMENT (
    appointment_id SERIAL PRIMARY KEY,
    caregiver_user_id INT NOT NULL REFERENCES CAREGIVER(caregiver_user_id) ON DELETE CASCADE,
    member_user_id INT NOT NULL REFERENCES MEMBER(member_user_id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    work_hours NUMERIC(4,2) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'confirmed', 'declined')) DEFAULT 'pending'
);


--insert values
INSERT INTO USERS (email, given_name, surname, city, phone_number, profile_description, password) VALUES
('arman@mail.com', 'Arman', 'Nurgaliyev', 'Astana', '+77001112233', 'Friendly caregiver', 'pass123'),
('amina@mail.com', 'Amina', 'Akhmetova', 'Almaty', '+77002223344', 'Experienced babysitter', 'pass123'),
('daniyar@mail.com', 'Daniyar', 'Kudaibergenov', 'Astana', '+77003334455', 'Love working with elderly', 'pass123'),
('saniya@mail.com', 'Saniya', 'Zhumagulova', 'Almaty', '+77004445566', 'Playful with kids', 'pass123'),
('zhanar@mail.com', 'Zhanar', 'Sarsembayeva', 'Astana', '+77005556677', 'Caring and patient', 'pass123'),
('erlan@mail.com', 'Erlan', 'Abdullin', 'Shymkent', '+77006667788', 'Experienced nanny', 'pass123'),
('gulnar@mail.com', 'Gulnar', 'Nurgalieva', 'Almaty', '+77007778899', 'Reliable caregiver', 'pass123'),
('nursultan@mail.com', 'Nursultan', 'Tulegenov', 'Astana', '+77008889900', 'Senior care specialist', 'pass123'),
('aliya@mail.com', 'Aliya', 'Beketova', 'Almaty', '+77009990011', 'Loves children', 'pass123'),
('aslan@mail.com', 'Aslan', 'Kassymov', 'Shymkent', '+77001001122', 'Experienced in childcare', 'pass123'),
('malika@mail.com', 'Malika', 'Kairatova', 'Astana', '+77001102233', 'Compassionate caregiver', 'pass123'),
('baybergen@mail.com', 'Baybergen', 'Yergaliyev', 'Almaty', '+77001203344', 'Reliable and punctual', 'pass123'),
('gulzhan@mail.com', 'Gulzhan', 'Bazarbayeva', 'Astana', '+77001304455', 'Trustworthy', 'pass123'),
('bekzat@mail.com', 'Bekzat', 'Abilov', 'Almaty', '+77001405566', 'Playmate for children', 'pass123'),
('dinara@mail.com', 'Dinara', 'Zhakslykova', 'Shymkent', '+77001506677', 'Elderly care expert', 'pass123'),
('murat@mail.com', 'Murat', 'Karimov', 'Astana', '+77001607788', 'Babysitter', 'pass123'),
('gulnara@mail.com', 'Gulnara', 'Orazbayeva', 'Almaty', '+77001708899', 'Patient with kids', 'pass123'),
('zhanibek@mail.com', 'Zhanibek', 'Akhmetov', 'Shymkent', '+77001809900', 'Caring', 'pass123'),
('aizhan@mail.com', 'Aizhan', 'Nurpeisova', 'Astana', '+77001901122', 'Experienced caregiver', 'pass123'),
('timur@mail.com', 'Timur', 'Beketov', 'Almaty', '+77002002233', 'Professional', 'pass123');

INSERT INTO CAREGIVER (caregiver_user_id, photo, gender, caregiving_type, hourly_rate) VALUES
(1,'photo1.jpg','Male','babysitter',8.5),
(2,'photo2.jpg','Female','babysitter',12),
(3,'photo3.jpg','Male','caregiver for elderly',15),
(4,'photo4.jpg','Female','playmate for children',10),
(5,'photo5.jpg','Female','babysitter',9.5),
(6,'photo6.jpg','Male','babysitter',11),
(7,'photo7.jpg','Female','caregiver for elderly',13),
(8,'photo8.jpg','Male','caregiver for elderly',14),
(9,'photo9.jpg','Female','playmate for children',10.5),
(10,'photo10.jpg','Male','babysitter',9),
(11,'photo11.jpg','Female','caregiver for elderly',12.5),
(12,'photo12.jpg','Male','babysitter',10),
(13,'photo13.jpg','Female','babysitter',11.5),
(14,'photo14.jpg','Male','playmate for children',9),
(15,'photo15.jpg','Female','caregiver for elderly',16),
(16,'photo16.jpg','Male','babysitter',8),
(17,'photo17.jpg','Female','playmate for children',10),
(18,'photo18.jpg','Male','caregiver for elderly',15),
(19,'photo19.jpg','Female','babysitter',9.5),
(20,'photo20.jpg','Male','babysitter',12);

INSERT INTO MEMBER (member_user_id, house_rules, dependent_description) VALUES
(1,'No pets, clean house','5-year-old son, likes painting'),
(2,'No smoking','3-year-old daughter, enjoys music'),
(3,'No pets, quiet','Grandmother, requires daily care'),
(4,'No smoking','7-year-old son, loves sports'),
(5,'No pets','Elderly father, needs supervision'),
(6,'No smoking','2-year-old daughter, likes drawing'),
(7,'No pets','Grandmother, mild dementia'),
(8,'No smoking','5-year-old daughter, likes dancing'),
(9,'No pets','6-year-old son, enjoys reading'),
(10,'No smoking','Elderly mother, mobility issues'),
(11,'No pets','4-year-old son, loves toys'),
(12,'No smoking','Elderly father, requires care'),
(13,'No pets','3-year-old daughter, playful'),
(14,'No smoking','Grandmother, mild dementia'),
(15,'No pets','Elderly mother, needs monitoring'),
(16,'No smoking','5-year-old son, active'),
(17,'No pets','6-year-old daughter, enjoys music'),
(18,'No smoking','Grandfather, requires daily care'),
(19,'No pets','4-year-old daughter, playful'),
(20,'No smoking','Elderly father, requires supervision');

INSERT INTO ADDRESS (member_user_id, house_number, street, town) VALUES
(1,'12','Kabanbay Batyr','Astana'),
(2,'24','Zhibek Zholy','Almaty'),
(3,'36','Pushkin','Astana'),
(4,'48','Abay','Shymkent'),
(5,'52','Seifullin','Astana'),
(6,'64','Kabanbay Batyr','Almaty'),
(7,'76','Dostyk','Astana'),
(8,'88','Tole Bi','Shymkent'),
(9,'90','Panfilov','Astana'),
(10,'102','Zhibek Zholy','Almaty'),
(11,'115','Abay','Astana'),
(12,'127','Kabanbay Batyr','Shymkent'),
(13,'139','Pushkin','Astana'),
(14,'141','Dostyk','Almaty'),
(15,'153','Seifullin','Astana'),
(16,'165','Tole Bi','Shymkent'),
(17,'177','Panfilov','Astana'),
(18,'189','Kabanbay Batyr','Almaty'),
(19,'201','Pushkin','Astana'),
(20,'213','Zhibek Zholy','Shymkent');

INSERT INTO JOB (member_user_id, required_caregiving_type, other_requirements) VALUES
(1,'babysitter','Soft-spoken, patient'),
(2,'babysitter','Creative, energetic'),
(3,'caregiver for elderly','Gentle, patient'),
(4,'playmate for children','Playful and fun'),
(5,'caregiver for elderly','Experienced, trustworthy'),
(6,'babysitter','Soft-spoken, attentive'),
(7,'caregiver for elderly','Friendly, patient'),
(8,'playmate for children','Creative, active'),
(9,'babysitter','Calm and patient'),
(10,'caregiver for elderly','Soft-spoken, kind'),
(11,'babysitter','Energetic and playful'),
(12,'caregiver for elderly','Trustworthy, gentle'),
(13,'babysitter','Soft-spoken'),
(14,'playmate for children','Fun and caring'),
(15,'caregiver for elderly','Patient and friendly'),
(16,'babysitter','Soft-spoken, creative'),
(17,'playmate for children','Active and kind'),
(18,'caregiver for elderly','Experienced and soft-spoken'),
(19,'babysitter','Gentle and patient'),
(20,'babysitter','Soft-spoken, attentive');


INSERT INTO JOB_APPLICATION (caregiver_user_id, job_id) VALUES
(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20);


INSERT INTO APPOINTMENT (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status) VALUES
(1,1,'2025-11-25','09:00',3,'confirmed'),
(2,2,'2025-11-26','10:00',2,'pending'),
(3,3,'2025-11-27','11:00',4,'declined'),
(4,4,'2025-11-28','12:00',3,'confirmed'),
(5,5,'2025-11-29','13:00',5,'pending'),
(6,6,'2025-11-30','14:00',2,'confirmed'),
(7,7,'2025-12-01','15:00',3,'pending'),
(8,8,'2025-12-02','16:00',4,'confirmed'),
(9,9,'2025-12-03','09:30',3,'declined'),
(10,10,'2025-12-04','10:30',2,'confirmed'),
(11,11,'2025-12-05','11:30',4,'pending'),
(12,12,'2025-12-06','12:30',3,'confirmed'),
(13,13,'2025-12-07','13:30',2,'declined'),
(14,14,'2025-12-08','14:30',3,'confirmed'),
(15,15,'2025-12-09','15:30',5,'pending'),
(16,16,'2025-12-10','16:30',2,'confirmed'),
(17,17,'2025-12-11','09:00',3,'pending'),
(18,18,'2025-12-12','10:00',4,'confirmed'),
(19,19,'2025-12-13','11:00',2,'declined'),
(20,20,'2025-12-14','12:00',3,'confirmed');

