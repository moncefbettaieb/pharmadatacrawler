-- Table: raw.pharmao

-- DROP TABLE IF EXISTS raw.pharmao;

CREATE TABLE IF NOT EXISTS raw.pharmao
(
    cip_code bigint NOT NULL DEFAULT nextval('pharmao_cip_code_seq'::regclass),
    title character varying COLLATE pg_catalog."default",
    brand character varying COLLATE pg_catalog."default",
    category character varying COLLATE pg_catalog."default",
    sub_category_1 character varying COLLATE pg_catalog."default",
    sub_category_2 character varying COLLATE pg_catalog."default",
    sub_category_3 character varying COLLATE pg_catalog."default",
    sub_category_4 double precision,
    description character varying COLLATE pg_catalog."default",
    composition character varying COLLATE pg_catalog."default",
    use character varying COLLATE pg_catalog."default",
    source character varying COLLATE pg_catalog."default",
    CONSTRAINT pharmao_pkey PRIMARY KEY (cip_code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS raw.pharmao
    OWNER to myuser;
-- Index: ix_pharmao_cip_code

CREATE INDEX IF NOT EXISTS ix_raw_pharmao_cip_code
    ON raw.pharmao USING btree
    (cip_code ASC NULLS LAST)
    TABLESPACE pg_default;
