CREATE SEQUENCE IF NOT EXISTS authentication_user_id_seq;
CREATE SEQUENCE IF NOT EXISTS contacts_contact_id_seq;
CREATE SEQUENCE IF NOT EXISTS events_event_id_seq;

CREATE TABLE IF NOT EXISTS authentication
(
    user_id integer NOT NULL DEFAULT nextval('authentication_user_id_seq'::regclass),
    login text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT authentication_pkey PRIMARY KEY (user_id),
    CONSTRAINT authentication_login_key UNIQUE (login)
);

CREATE TABLE IF NOT EXISTS contacts
(
    contact_id integer NOT NULL DEFAULT nextval('contacts_contact_id_seq'::regclass),
    owner integer NOT NULL,
    surname text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    patronymic text COLLATE pg_catalog."default",
    birthday text COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    street text COLLATE pg_catalog."default",
    house_number text COLLATE pg_catalog."default",
    apartment_number text COLLATE pg_catalog."default",
    phone_number text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT contacts_pkey PRIMARY KEY (contact_id),
    CONSTRAINT phone UNIQUE (owner, phone_number),
    CONSTRAINT owner_user_id FOREIGN KEY (owner)
        REFERENCES authentication (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

CREATE TABLE IF NOT EXISTS events
(
    event_id integer NOT NULL DEFAULT nextval('events_event_id_seq'::regclass),
    owner integer NOT NULL,
    date text COLLATE pg_catalog."default" NOT NULL,
    event_list text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT events_pkey PRIMARY KEY (event_id),
    CONSTRAINT owner_user_id FOREIGN KEY (owner)
        REFERENCES authentication (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);
