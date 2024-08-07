CREATE TABLE "objects" (
  "object_id" varchar(32) PRIMARY KEY,
  "object_number" varchar(10) UNIQUE,
  "location" point DEFAULT null,
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "boreholes" (
  "borehole_id" varchar(32) PRIMARY KEY,
  "borehole_name" varchar(50),
  "object_id" varchar(32),
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "samples" (
  "sample_id" varchar(32) PRIMARY KEY,
  "borehole_id" varchar(32),
  "laboratory_number" varchar(50),
  "soil_type" varchar(500),
  "properties" jsonb DEFAULT null,
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "tests" (
  "test_id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "sample_id" varchar(32),
  "test_type_id" int,
  "timestamp" timestamp DEFAULT (now()),
  "test_params" jsonb DEFAULT null,
  "test_results" jsonb DEFAULT null,
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "files" (
  "file_id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "test_id" bigint,
  "upload" timestamp DEFAULT (now()),
  "key" varchar(500),
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "test_types" (
  "test_type_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "test_type" varchar(500) UNIQUE,
  "description" varchar(500) DEFAULT null
);

CREATE TABLE "parameters_titles" (
  "param_id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "param_name" varchar(50),
  "param_title" varchar(500),
  "description" varchar(500) DEFAULT null
);

COMMENT ON COLUMN "objects"."object_id" IS 'from EngGeo';

COMMENT ON COLUMN "boreholes"."borehole_id" IS 'from EngGeo';

COMMENT ON COLUMN "samples"."sample_id" IS 'from EngGeo';

ALTER TABLE "boreholes" ADD FOREIGN KEY ("object_id") REFERENCES "objects" ("object_id");

ALTER TABLE "samples" ADD FOREIGN KEY ("borehole_id") REFERENCES "boreholes" ("borehole_id");

ALTER TABLE "tests" ADD FOREIGN KEY ("sample_id") REFERENCES "samples" ("sample_id");

ALTER TABLE "tests" ADD FOREIGN KEY ("test_type_id") REFERENCES "test_types" ("test_type_id");

ALTER TABLE "files" ADD FOREIGN KEY ("test_id") REFERENCES "tests" ("test_id");
