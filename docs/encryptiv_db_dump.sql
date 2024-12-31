--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity (
    activity_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    item_id uuid NOT NULL,
    item_type character varying(10) NOT NULL,
    operations text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT activity_item_type_check CHECK (((item_type)::text = ANY ((ARRAY['file'::character varying, 'folder'::character varying])::text[])))
);


ALTER TABLE public.activity OWNER TO postgres;

--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    file_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    parent_id uuid,
    name character varying NOT NULL,
    extension character varying(10),
    size integer NOT NULL,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    opened timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    description text,
    deleted boolean DEFAULT false
);


ALTER TABLE public.files OWNER TO postgres;

--
-- Name: folders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.folders (
    folder_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    parent_id uuid,
    name character varying NOT NULL,
    total_size integer DEFAULT 0,
    opened timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    description text,
    deleted boolean DEFAULT false
);


ALTER TABLE public.folders OWNER TO postgres;

--
-- Name: pins_suggestions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pins_suggestions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    type character varying(10) NOT NULL,
    mode smallint NOT NULL,
    CONSTRAINT pins_suggestions_mode_check CHECK ((mode = ANY (ARRAY[0, 1]))),
    CONSTRAINT pins_suggestions_type_check CHECK (((type)::text = ANY ((ARRAY['file'::character varying, 'folder'::character varying])::text[])))
);


ALTER TABLE public.pins_suggestions OWNER TO postgres;

--
-- Name: recycle_bin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recycle_bin (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    type character varying(10) NOT NULL,
    deletion_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT recycle_bin_type_check CHECK (((type)::text = ANY ((ARRAY['file'::character varying, 'folder'::character varying])::text[])))
);


ALTER TABLE public.recycle_bin OWNER TO postgres;

--
-- Data for Name: activity; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity (activity_id, user_id, item_id, item_type, operations, "timestamp") FROM stdin;
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.files (file_id, user_id, parent_id, name, extension, size, modified, opened, created, description, deleted) FROM stdin;
\.


--
-- Data for Name: folders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.folders (folder_id, user_id, parent_id, name, total_size, opened, created, description, deleted) FROM stdin;
\.


--
-- Data for Name: pins_suggestions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pins_suggestions (id, user_id, type, mode) FROM stdin;
\.


--
-- Data for Name: recycle_bin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recycle_bin (id, user_id, type, deletion_time) FROM stdin;
\.


--
-- Name: activity activity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (activity_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- Name: folders folders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (folder_id);


--
-- Name: pins_suggestions pins_suggestions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pins_suggestions
    ADD CONSTRAINT pins_suggestions_pkey PRIMARY KEY (id);


--
-- Name: recycle_bin recycle_bin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycle_bin
    ADD CONSTRAINT recycle_bin_pkey PRIMARY KEY (id);


--
-- Name: activity activity_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.folders(folder_id) ON DELETE CASCADE;


--
-- Name: activity activity_item_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_item_id_fkey1 FOREIGN KEY (item_id) REFERENCES public.files(file_id) ON DELETE CASCADE;


--
-- Name: files files_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.folders(folder_id) ON DELETE CASCADE;


--
-- Name: folders folders_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders
    ADD CONSTRAINT folders_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.folders(folder_id) ON DELETE CASCADE;


--
-- Name: pins_suggestions pins_suggestions_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pins_suggestions
    ADD CONSTRAINT pins_suggestions_id_fkey FOREIGN KEY (id) REFERENCES public.folders(folder_id) ON DELETE CASCADE;


--
-- Name: pins_suggestions pins_suggestions_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pins_suggestions
    ADD CONSTRAINT pins_suggestions_id_fkey1 FOREIGN KEY (id) REFERENCES public.files(file_id) ON DELETE CASCADE;


--
-- Name: recycle_bin recycle_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycle_bin
    ADD CONSTRAINT recycle_bin_id_fkey FOREIGN KEY (id) REFERENCES public.folders(folder_id) ON DELETE CASCADE;


--
-- Name: recycle_bin recycle_bin_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycle_bin
    ADD CONSTRAINT recycle_bin_id_fkey1 FOREIGN KEY (id) REFERENCES public.files(file_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--