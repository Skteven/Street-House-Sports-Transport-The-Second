import sqlite3

connection = sqlite3.connect('transport.db')
connection.row_factory = sqlite3.Row

query = 'DROP TABLE If EXISTS Timetable;'
result = connection.execute(query)

query = 'CREATE TABLE Timetable (TimetableID INTEGER PRIMARY KEY, FullName varchar(255), PNumber varchar(10), Date DATE, Location INTEGER, Other varchar(255), DropOff varchar(20), PickUp varchar(20), AddInfo text, Submittedby TEXT);'
result = connection.execute(query)

query = "INSERT INTO Timetable (FullName,PNumber,Date,Location,Other,DropOff,PickUp,AddInfo) VALUES ('Lamine Yamal','04121415161','21/06/2025',2,'N/a','9:30am','2:00pm','Stinky Boots');"
result = connection.execute(query)

query = "INSERT INTO Timetable (FullName,PNumber,Date,Location,Other,DropOff,PickUp,AddInfo) VALUES ('James Bond','007','21/06/2025',1,'Opera House','2:30am','2:00am','Secret Gadget');"
result = connection.execute(query)

connection.commit()

query = 'DROP TABLE If EXISTS Location;'
result = connection.execute(query)

query = 'CREATE TABLE Location (LocationID INTEGER PRIMARY KEY,LocationName varchar(255), Address varchar(255));'
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Other',' ');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Cranbrook Junior School','6 Kent Rd, Rose Bay NSW 2029');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Lyne Park Tennis Court','Vickery Avenue, New South Head Rd, Rose Bay NSW 2029');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Knox Grammar School','2 Borambil St, Wahroonga NSW 2076');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Trinity Grammar School','119 Prospect Rd, Summer Hill NSW 2130');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Barker Collage','9 The Avenue, Hornsby NSW 2077');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('St Aloysius','47 Upper Pitt St, Kirribilli NSW 2061');"
result = connection.execute(query)

query = "INSERT INTO Location (LocationName,Address) VALUES ('Waverly Collage','131 Birrell St, Waverley NSW 2024');"
result = connection.execute(query)

connection.commit()

query = 'DROP TABLE If EXISTS User;'
result = connection.execute(query)

query = 'CREATE TABLE User (Email varchar(25) PRIMARY KEY, FName varchar (255), SName varchar (255), PNumber varchar(10), Username varchar(25), Role INTEGER, Password varchar(255));'
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('kongste2025@student.cranbrook.nsw.edu.au','Steve','Kong','0428395618','Steve',3,'studentpass');"
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('willitom2025@student.cranbrook.nsw.edu.au','Biggy','Williams','0463937588','Biggy',3,'studentpass');"
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('bondjam2025@cranbrook.nsw.edu.au','James','Bond','0438293048','007',2,'staffpass');"
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('trunaga2025@cranbrook.nsw.edu.au','Agatha','Trunchbull','0473529574','Meanie',2,'staffpass');"
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('dwayjoh2025@cranbrook.nsw.edu.au','Dwayne','Johnson','0493726485','Rock',1,'boardingpass');"
result = connection.execute(query)

query = "INSERT INTO User (Email,FName,SName,PNumber,Username,Role,Password) VALUES ('antalb2025@cranbrook.nsw.edu.au','Anthony','Albanese','046493720194','Albo',1,'boardingpass');"
result = connection.execute(query)

connection.commit()

query = 'DROP TABLE If EXISTS Role;'
result = connection.execute(query)

query = 'CREATE TABLE Role (RoleID INTEGER PRIMARY KEY,RoleName varchar(255));'
result = connection.execute(query)

query = "INSERT INTO Role (RoleID, RoleName) VALUES (1, 'Boarding Staff');"
result = connection.execute(query)

query = "INSERT INTO Role (RoleID, RoleName) VALUES (2, 'Staff');"
result = connection.execute(query)

query = "INSERT INTO Role (RoleID, RoleName) VALUES (3, 'Student');"
result = connection.execute(query)

connection.commit()
