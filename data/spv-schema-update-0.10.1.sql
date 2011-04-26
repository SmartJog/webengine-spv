SET search_path = spv, pg_catalog;

ALTER TABLE ONLY checks_group   ADD CONSTRAINT checks_group_grp_id_chk_id_uniq_key UNIQUE (chk_id, grp_id);
ALTER TABLE ONLY objects_group  ADD CONSTRAINT objects_group_grp_id_obj_id_uniq_key UNIQUE (obj_id, grp_id);
