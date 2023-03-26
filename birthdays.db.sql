BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "bdays" (
	"ID"	INTEGER NOT NULL,
	"Name"	TEXT NOT NULL,
	"Date"	TEXT NOT NULL,
	"Gift"	BOOLEAN NOT NULL,
	"Reminder"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (1,'Axel','1998-02-06','Yes',3);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (4,'Test','2000-03-23','Yes',2);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (5,'Test2','2010-03-22','No',0);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (7,'tt','2023-01-01','No',0);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (8,'discord1','2022-04-08','No',0);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (9,'discord1','2022-04-08','No',0);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (10,'discord3','2022-04-08','Yes',0);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (11,'discord4','2022-04-08','Yes',1);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (12,'discord5','2022-04-01','No',2);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (13,'tt','2022-03-25','Yes',2);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (16,'hejhej','1998-03-27','Yes',4);
INSERT INTO "bdays" ("ID","Name","Date","Gift","Reminder") VALUES (17,'t4','2001-03-25','No',1);
COMMIT;
