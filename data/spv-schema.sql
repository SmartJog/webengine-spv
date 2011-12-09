--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: spv; Type: SCHEMA; Schema: -; Owner: spv
--

CREATE SCHEMA spv;


ALTER SCHEMA spv OWNER TO spv;

--
-- Name: SCHEMA spv; Type: COMMENT; Schema: -; Owner: spv
--

COMMENT ON SCHEMA spv IS 'Supervision schema';


SET search_path = spv, pg_catalog;

--
-- Name: check_infos_insert_fn(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION check_infos_insert_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	-- upsert
    if (SELECT count(chk_id) FROM check_infos WHERE chk_id=NEW.chk_id AND key=NEW.key) = 0 THEN
        RETURN NEW;
    END IF;
    UPDATE check_infos SET value=NEW.value WHERE key=NEW.key AND chk_id=NEW.chk_id;
    RETURN OLD;
END;
$$;


ALTER FUNCTION spv.check_infos_insert_fn() OWNER TO spv;

--
-- Name: check_insert(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION check_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    EXECUTE new_check(NEW.chk_id, NEW.grp_id);
    RETURN NEW;
END;$$;


ALTER FUNCTION spv.check_insert() OWNER TO spv;

--
-- Name: insert_spv(integer, character varying, character varying); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION insert_spv(integer, character varying, character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        _status_id      ALIAS FOR $1;
        _key            ALIAS FOR $2;
        _value          ALIAS FOR $3;
        _sinfo_id        INTEGER;
    BEGIN
        IF _status_id IS NULL OR _key IS NULL THEN -- Allow _value to be null
            RETURN false;
        END IF;
        SELECT INTO _sinfo_id sinfo_id FROM status_infos WHERE status_id = _status_id AND "key" = _key;
        IF _sinfo_id IS NULL THEN
           INSERT INTO status_infos (status_id, key, value) VALUES (_status_id, _key, _value);
        ELSE
           UPDATE status_infos SET value = _value WHERE sinfo_id = _sinfo_id;
        END IF;
        RETURN true;
    END;
$_$;


ALTER FUNCTION spv.insert_spv(integer, character varying, character varying) OWNER TO spv;

--
-- Name: new_check(integer, integer); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION new_check(in_cg_id integer, in_grp_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  object RECORD;
BEGIN
  FOR object IN SELECT * FROM objects_group NATURAL JOIN groups WHERE grp_id=in_grp_id LOOP
    INSERT INTO status(cg_id,og_id,seq_id) VALUES (in_cg_id, object.og_id, 0);
  END LOOP;
END;$$;


ALTER FUNCTION spv.new_check(in_cg_id integer, in_grp_id integer) OWNER TO spv;

--
-- Name: new_object(integer, integer); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION new_object(in_og_id integer, in_grp_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  check RECORD;
BEGIN
  FOR check IN SELECT * FROM checks_group NATURAL JOIN groups WHERE grp_id=in_grp_id LOOP
    INSERT INTO status(cg_id,og_id,seq_id) VALUES (check.cg_id, in_og_id, 0);
  END LOOP;
END;$$;


ALTER FUNCTION spv.new_object(in_og_id integer, in_grp_id integer) OWNER TO spv;

--
-- Name: object_infos_insert_fn(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION object_infos_insert_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	-- upsert
    if (SELECT count(obj_id) FROM object_infos WHERE obj_id=NEW.obj_id AND key=NEW.key) = 0 THEN
        RETURN NEW;
    END IF;
    UPDATE object_infos SET value=NEW.value WHERE key=NEW.key AND obj_id=NEW.obj_id;
    RETURN OLD;
END;
$$;


ALTER FUNCTION spv.object_infos_insert_fn() OWNER TO spv;

--
-- Name: object_insert(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION object_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  EXECUTE new_object(NEW.obj_id, NEW.grp_id);
  RETURN NEW;
END;$$;


ALTER FUNCTION spv.object_insert() OWNER TO spv;

--
-- Name: status_infos_insert_fn(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION status_infos_insert_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	-- upsert
    if (SELECT count(status_id) FROM status_infos WHERE status_id=NEW.status_id AND key=NEW.key) = 0 THEN
        RETURN NEW;
    END IF;
    UPDATE status_infos SET value=NEW.value WHERE key=NEW.key AND status_id=NEW.status_id;
    RETURN OLD;
END;
$$;


ALTER FUNCTION spv.status_infos_insert_fn() OWNER TO spv;

--
-- Name: status_update(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION status_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$DECLARE
    repeat INTEGER;
    seconds VARCHAR;
BEGIN
    IF OLD.check_status != NEW.check_status THEN
            NEW.status_changed_date=now();
    END IF;
    RETURN NEW;
END;$$;


ALTER FUNCTION spv.status_update() OWNER TO spv;

--
-- Name: update_modif_date(); Type: FUNCTION; Schema: spv; Owner: spv
--

CREATE FUNCTION update_modif_date() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    NEW.modification_date = now();
    RETURN NEW;
END$$;


ALTER FUNCTION spv.update_modif_date() OWNER TO spv;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: checks; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE checks (
    chk_id integer DEFAULT nextval(('spv.checks_chk_id_seq'::text)::regclass) NOT NULL,
    plugin character varying NOT NULL,
    plugin_check character varying NOT NULL,
    name character varying NOT NULL,
    repeat integer NOT NULL,
    repeat_on_error integer NOT NULL,
    CONSTRAINT strictly_positive_time CHECK (((repeat > 0) AND (repeat_on_error > 0)))
);


ALTER TABLE spv.checks OWNER TO spv;

--
-- Name: COLUMN checks.name; Type: COMMENT; Schema: spv; Owner: spv
--

COMMENT ON COLUMN checks.name IS 'User visible string';


--
-- Name: checks_chk_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE checks_chk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.checks_chk_id_seq OWNER TO spv;

--
-- Name: checks_group; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE checks_group (
    cg_id integer DEFAULT nextval(('spv.checks_group_cg_id_seq'::text)::regclass) NOT NULL,
    chk_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE spv.checks_group OWNER TO spv;

--
-- Name: checks_group_cg_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE checks_group_cg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.checks_group_cg_id_seq OWNER TO spv;

--
-- Name: groups; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE groups (
    grp_id integer DEFAULT nextval(('spv.groups_grp_id_seq'::text)::regclass) NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE spv.groups OWNER TO spv;

--
-- Name: COLUMN groups.name; Type: COMMENT; Schema: spv; Owner: spv
--

COMMENT ON COLUMN groups.name IS 'User visible string';


--
-- Name: objects; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE objects (
    obj_id integer DEFAULT nextval(('spv.objects_obj_id_seq'::text)::regclass) NOT NULL,
    address character varying NOT NULL,
    creation_date date DEFAULT now() NOT NULL,
    modification_date date
);


ALTER TABLE spv.objects OWNER TO spv;

--
-- Name: objects_group; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE objects_group (
    og_id integer DEFAULT nextval(('spv.objects_group_og_id_seq'::text)::regclass) NOT NULL,
    obj_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE spv.objects_group OWNER TO spv;

--
-- Name: status; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE status (
    status_id integer DEFAULT nextval(('spv.status_status_id_seq'::text)::regclass) NOT NULL,
    cg_id integer NOT NULL,
    og_id integer NOT NULL,
    check_status character varying DEFAULT 'INITIAL'::character varying NOT NULL,
    check_message character varying,
    last_check timestamp without time zone DEFAULT now(),
    next_check timestamp without time zone DEFAULT now(),
    seq_id integer DEFAULT 0 NOT NULL,
    status_acknowledged_date timestamp without time zone DEFAULT now(),
    status_changed_date timestamp without time zone DEFAULT now(),
    CONSTRAINT positive_seqence CHECK ((seq_id >= 0))
);


ALTER TABLE spv.status OWNER TO spv;

--
-- Name: COLUMN status.last_check; Type: COMMENT; Schema: spv; Owner: spv
--

COMMENT ON COLUMN status.last_check IS 'When was the check last fetched';


--
-- Name: COLUMN status.next_check; Type: COMMENT; Schema: spv; Owner: spv
--

COMMENT ON COLUMN status.next_check IS 'When will the check be performed again';


--
-- Name: checks_list; Type: VIEW; Schema: spv; Owner: spv
--

CREATE VIEW checks_list AS
    SELECT checks.plugin_check, checks.plugin, groups.grp_id, status.last_check, status.next_check, status.check_status, status.check_message, status.cg_id, status.og_id, status.seq_id, status.status_id, objects.address, groups.name AS group_name, checks.name AS check_name FROM (((((objects NATURAL JOIN objects_group) NATURAL JOIN status) NATURAL JOIN checks_group) NATURAL JOIN checks) LEFT JOIN groups ON ((checks_group.grp_id = groups.grp_id)));


ALTER TABLE spv.checks_list OWNER TO spv;

--
-- Name: groups_grp_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE groups_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.groups_grp_id_seq OWNER TO spv;

--
-- Name: object_infos; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE object_infos (
    oinfo_id integer DEFAULT nextval(('spv.object_infos_oinfo_id_seq'::text)::regclass) NOT NULL,
    obj_id integer NOT NULL,
    key character varying(4096) NOT NULL,
    value character varying(4096),
    creation_date timestamp without time zone DEFAULT now(),
    modification_date timestamp without time zone DEFAULT now()
);


ALTER TABLE spv.object_infos OWNER TO spv;

--
-- Name: object_infos_oinfo_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE object_infos_oinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.object_infos_oinfo_id_seq OWNER TO spv;

--
-- Name: objects_group_og_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE objects_group_og_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.objects_group_og_id_seq OWNER TO spv;

--
-- Name: objects_obj_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE objects_obj_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.objects_obj_id_seq OWNER TO spv;

--
-- Name: status_infos; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE status_infos (
    sinfo_id integer DEFAULT nextval(('spv.status_infos_sinfo_id_seq'::text)::regclass) NOT NULL,
    status_id integer NOT NULL,
    key character varying(4096) NOT NULL,
    value character varying(4096),
    creation_date timestamp without time zone DEFAULT now(),
    modification_date timestamp without time zone DEFAULT now()
);


ALTER TABLE spv.status_infos OWNER TO spv;

--
-- Name: check_infos; Type: TABLE; Schema: spv; Owner: spv; Tablespace: 
--

CREATE TABLE check_infos (
    cinfo_id integer DEFAULT nextval(('spv.check_infos_cinfo_id_seq'::text)::regclass) NOT NULL,
    chk_id integer NOT NULL,
    key character varying(4096) NOT NULL,
    value character varying(4096),
    creation_date timestamp without time zone DEFAULT now(),
    modification_date timestamp without time zone DEFAULT now()
);


ALTER TABLE spv.check_infos OWNER TO spv;

--
-- Name: check_infos_cinfo_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE check_infos_cinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.check_infos_cinfo_id_seq OWNER TO spv;


--
-- Name: status_infos_sinfo_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE status_infos_sinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.status_infos_sinfo_id_seq OWNER TO spv;

--
-- Name: status_infos_view; Type: VIEW; Schema: spv; Owner: spv
--

CREATE VIEW status_infos_view AS
    SELECT status_infos.sinfo_id, status_infos.status_id, status_infos.key, status_infos.value, status_infos.creation_date, status_infos.modification_date FROM status_infos;


ALTER TABLE spv.status_infos_view OWNER TO spv;

--
-- Name: status_status_id_seq; Type: SEQUENCE; Schema: spv; Owner: spv
--

CREATE SEQUENCE status_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE spv.status_status_id_seq OWNER TO spv;

--
-- Name: cg_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY checks_group
    ADD CONSTRAINT cg_id_pkey PRIMARY KEY (cg_id);


--
-- Name: check_infos_check_key_uniq; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY check_infos
    ADD CONSTRAINT check_infos_check_key_uniq UNIQUE (chk_id, key);


--
-- Name: checks_group_uniq_key; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY checks_group
    ADD CONSTRAINT checks_group_uniq_key UNIQUE (chk_id, grp_id);


--
-- Name: chk_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY checks
    ADD CONSTRAINT chk_id_pkey PRIMARY KEY (chk_id);


--
-- Name: cinfo_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY check_infos
    ADD CONSTRAINT cinfo_id_pkey PRIMARY KEY (cinfo_id);


--
-- Name: grp_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT grp_id_pkey PRIMARY KEY (grp_id);


--
-- Name: obj_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY objects
    ADD CONSTRAINT obj_id_pkey PRIMARY KEY (obj_id);


--
-- Name: object_infos_object_key_uniq; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY object_infos
    ADD CONSTRAINT object_infos_object_key_uniq UNIQUE (obj_id, key);


--
-- Name: objects_group_uniq_key; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY objects_group
    ADD CONSTRAINT objects_group_uniq_key UNIQUE (obj_id, grp_id);


--
-- Name: og_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY objects_group
    ADD CONSTRAINT og_id_pkey PRIMARY KEY (og_id);


--
-- Name: oinfo_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY object_infos
    ADD CONSTRAINT oinfo_id_pkey PRIMARY KEY (oinfo_id);


--
-- Name: plugin_checks_unique; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY checks
    ADD CONSTRAINT plugin_checks_unique UNIQUE (plugin, plugin_check, name);


--
-- Name: sinfo_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY status_infos
    ADD CONSTRAINT sinfo_id_pkey PRIMARY KEY (sinfo_id);


--
-- Name: status_id_pkey; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT status_id_pkey PRIMARY KEY (status_id);


--
-- Name: status_infos_status_key_uniq; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY status_infos
    ADD CONSTRAINT status_infos_status_key_uniq UNIQUE (status_id, key);


--
-- Name: status_uniq_key; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT status_uniq_key UNIQUE (status_id, cg_id, og_id);


--
-- Name: uniq_address; Type: CONSTRAINT; Schema: spv; Owner: spv; Tablespace: 
--

ALTER TABLE ONLY objects
    ADD CONSTRAINT uniq_address UNIQUE (address);


--
-- Name: status_infos_status_key_idx; Type: INDEX; Schema: spv; Owner: spv; Tablespace: 
--

CREATE INDEX status_infos_status_key_idx ON status_infos USING btree (key);


--
-- Name: status_infos_view_rule; Type: RULE; Schema: spv; Owner: spv
--

CREATE RULE status_infos_view_rule AS ON INSERT TO status_infos_view DO INSTEAD SELECT insert_spv(new.status_id, new.key, new.value) AS insert_spv;


--
-- Name: check_infos_insert_trg; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER check_infos_insert_trg
    BEFORE INSERT ON check_infos
    FOR EACH ROW
    EXECUTE PROCEDURE check_infos_insert_fn();


--
-- Name: check_infos_update_modif_date; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER check_infos_update_modif_date
    BEFORE UPDATE ON check_infos
    FOR EACH ROW
    EXECUTE PROCEDURE update_modif_date();


--
-- Name: checks_group_insert; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER checks_group_insert
    AFTER INSERT ON checks_group
    FOR EACH ROW
    EXECUTE PROCEDURE check_insert();


--
-- Name: object_infos_insert_trg; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER object_infos_insert_trg
    BEFORE INSERT ON object_infos
    FOR EACH ROW
    EXECUTE PROCEDURE object_infos_insert_fn();


--
-- Name: object_infos_update_modif_date; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER object_infos_update_modif_date
    BEFORE UPDATE ON object_infos
    FOR EACH ROW
    EXECUTE PROCEDURE update_modif_date();


--
-- Name: objects_group_insert; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER objects_group_insert
    AFTER INSERT ON objects_group
    FOR EACH ROW
    EXECUTE PROCEDURE object_insert();


--
-- Name: status_infos_insert_trg; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER status_infos_insert_trg
    BEFORE INSERT ON status_infos
    FOR EACH ROW
    EXECUTE PROCEDURE status_infos_insert_fn();


--
-- Name: status_infos_update_modif_date; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER status_infos_update_modif_date
    BEFORE UPDATE ON status_infos
    FOR EACH ROW
    EXECUTE PROCEDURE update_modif_date();


--
-- Name: status_update_trigger; Type: TRIGGER; Schema: spv; Owner: spv
--

CREATE TRIGGER status_update_trigger
    BEFORE UPDATE ON status
    FOR EACH ROW
    EXECUTE PROCEDURE status_update();


--
-- Name: cg_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY status
    ADD CONSTRAINT cg_id_fk FOREIGN KEY (cg_id) REFERENCES checks_group(cg_id) ON DELETE CASCADE;


--
-- Name: check_infos_chk_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY check_infos
    ADD CONSTRAINT check_infos_chk_id_fk FOREIGN KEY (chk_id) REFERENCES checks(chk_id) ON DELETE CASCADE;


--
-- Name: chk_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY checks_group
    ADD CONSTRAINT chk_id_fk FOREIGN KEY (chk_id) REFERENCES checks(chk_id) ON DELETE CASCADE;


--
-- Name: grp_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY checks_group
    ADD CONSTRAINT grp_id_fk FOREIGN KEY (grp_id) REFERENCES groups(grp_id) ON DELETE CASCADE;


--
-- Name: grp_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY objects_group
    ADD CONSTRAINT grp_id_fk FOREIGN KEY (grp_id) REFERENCES groups(grp_id) ON DELETE CASCADE;


--
-- Name: obj_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY objects_group
    ADD CONSTRAINT obj_id_fk FOREIGN KEY (obj_id) REFERENCES objects(obj_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: object_infos_obj_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY object_infos
    ADD CONSTRAINT object_infos_obj_id_fk FOREIGN KEY (obj_id) REFERENCES objects(obj_id) ON DELETE CASCADE;


--
-- Name: og_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY status
    ADD CONSTRAINT og_id_fk FOREIGN KEY (og_id) REFERENCES objects_group(og_id) ON DELETE CASCADE;


--
-- Name: status_infos_status_id_fk; Type: FK CONSTRAINT; Schema: spv; Owner: spv
--

ALTER TABLE ONLY status_infos
    ADD CONSTRAINT status_infos_status_id_fk FOREIGN KEY (status_id) REFERENCES status(status_id) ON DELETE CASCADE;


--
-- Name: spv; Type: ACL; Schema: -; Owner: spv
--

REVOKE ALL ON SCHEMA spv FROM PUBLIC;
REVOKE ALL ON SCHEMA spv FROM spv;
GRANT ALL ON SCHEMA spv TO spv;


--
-- Name: checks; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE checks FROM PUBLIC;
REVOKE ALL ON TABLE checks FROM spv;
GRANT ALL ON TABLE checks TO spv;


--
-- Name: checks_group; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE checks_group FROM PUBLIC;
REVOKE ALL ON TABLE checks_group FROM spv;
GRANT ALL ON TABLE checks_group TO spv;


--
-- Name: groups; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE groups FROM PUBLIC;
REVOKE ALL ON TABLE groups FROM spv;
GRANT ALL ON TABLE groups TO spv;


--
-- Name: objects; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE objects FROM PUBLIC;
REVOKE ALL ON TABLE objects FROM spv;
GRANT ALL ON TABLE objects TO spv;


--
-- Name: objects_group; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE objects_group FROM PUBLIC;
REVOKE ALL ON TABLE objects_group FROM spv;
GRANT ALL ON TABLE objects_group TO spv;


--
-- Name: status; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE status FROM PUBLIC;
REVOKE ALL ON TABLE status FROM spv;
GRANT ALL ON TABLE status TO spv;

--
-- Name: status_infos; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE status_infos FROM PUBLIC;
REVOKE ALL ON TABLE status_infos FROM spv;
GRANT ALL ON TABLE status_infos TO spv;


--
-- Name: check_infos; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE check_infos FROM PUBLIC;
REVOKE ALL ON TABLE check_infos FROM spv;
GRANT ALL ON TABLE check_infos TO spv;


--
-- Name: check_infos_cinfo_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE check_infos_cinfo_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE check_infos_cinfo_id_seq FROM spv;
GRANT ALL ON SEQUENCE check_infos_cinfo_id_seq TO spv;


--
-- Name: checks_chk_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE checks_chk_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE checks_chk_id_seq FROM spv;
GRANT ALL ON SEQUENCE checks_chk_id_seq TO spv;


--
-- Name: checks_group_cg_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE checks_group_cg_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE checks_group_cg_id_seq FROM spv;
GRANT ALL ON SEQUENCE checks_group_cg_id_seq TO spv;


--
-- Name: checks_list; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE checks_list FROM PUBLIC;
REVOKE ALL ON TABLE checks_list FROM spv;
GRANT ALL ON TABLE checks_list TO spv;


--
-- Name: groups_grp_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE groups_grp_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE groups_grp_id_seq FROM spv;
GRANT ALL ON SEQUENCE groups_grp_id_seq TO spv;


--
-- Name: object_infos; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON TABLE object_infos FROM PUBLIC;
REVOKE ALL ON TABLE object_infos FROM spv;
GRANT ALL ON TABLE object_infos TO spv;


--
-- Name: object_infos_oinfo_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE object_infos_oinfo_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE object_infos_oinfo_id_seq FROM spv;
GRANT ALL ON SEQUENCE object_infos_oinfo_id_seq TO spv;


--
-- Name: objects_group_og_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE objects_group_og_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE objects_group_og_id_seq FROM spv;
GRANT ALL ON SEQUENCE objects_group_og_id_seq TO spv;


--
-- Name: objects_obj_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE objects_obj_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE objects_obj_id_seq FROM spv;
GRANT ALL ON SEQUENCE objects_obj_id_seq TO spv;


--
-- Name: status_infos_sinfo_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE status_infos_sinfo_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE status_infos_sinfo_id_seq FROM spv;
GRANT ALL ON SEQUENCE status_infos_sinfo_id_seq TO spv;


--
-- Name: status_status_id_seq; Type: ACL; Schema: spv; Owner: spv
--

REVOKE ALL ON SEQUENCE status_status_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE status_status_id_seq FROM spv;
GRANT ALL ON SEQUENCE status_status_id_seq TO spv;


--
-- PostgreSQL database dump complete
--

