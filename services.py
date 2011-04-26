from webengine.utils.decorators import exportable
from webengine.utils.decorators import webengine_pgconn
from webengine.utils.log import logger
import sjutils

GROUP_FIELDS        = ['groups.grp_id', 'groups.name']
OBJECT_FIELDS       = ['objects.obj_id', 'objects.address', 'objects.creation_date']
CHECK_FIELDS        = ['checks.chk_id', 'checks.plugin', 'checks.plugin_check', 'checks.name', 'checks.repeat', 'checks.repeat_on_error']
STATUS_FIELDS       = ['status.status_id', 'status.cg_id', 'status.check_status', 'status.check_message', 'status.last_check', 'status.next_check', 'status.status_changed_date', 'status.status_acknowledged_date', 'status.seq_id']
OBJECT_INFOS_FIELDS = ['object_infos.oinfo_id', 'object_infos.obj_id', 'object_infos.key', 'object_infos.value']
CHECK_INFOS_FIELDS  = ['check_infos.cinfo_id', 'check_infos.chk_id', 'check_infos.key', 'check_infos.value']
STATUS_INFOS_FIELDS = ['status_infos.sinfo_id', 'status_infos.status_id', 'status_infos.key', 'status_infos.value']

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def get_checks(pg_manager, ctx_list, _request, params=None):
    """ Deprecated: use get_status instead
    Returns checks, groups and objects from supervision database.

    @params: dictionary with parameters allowing fine grained selection of items from the SPV database
             paramaters can be one of the following:
        'status' (String or String List) get checks with the given status
        'group_name' (String or String List) name(s) of the group(s) to get checks for
        'object_address' (String) address of the object to get
        'plugin_name' (String) name of the plugin to get checks for
        'plugin_check' (String) name of the check to get
        'group_id' (Integer or Integer List) return group(s) whose id(s) is(are) the one(s) specified
        'check_id' (Integer) return check whose id is check_id
        'status_id' (Integer) return status whose id is status_id
        'limit' (Integer) maximum number of checks to get
        'get_status_infos' (Boolean, default False) get additional informations attached to the requested status
        'get_object_infos' (Boolean, default False) get additional informations attached to the requested objects
        'get_check_infos' (Boolean, default False) get additional informations attached to the request checks
        'get_check_groups' (Boolean, default False) get per check groups
        'get_detailed_infos' (Boolean, default True) get detailed informations (returns dictionnary with DB entries ID, etc..)
        'next_check_expired' (Boolean, default False) require check that are new
        'update_next_check' (Boolean, default False) schedule next iteration of the checks
    @returns: a dictionary containing list of status, groups and objects
    {
        'checks': {
            @chk_id: {
                'chk_id'        : Integer,
                'name'          : String,
                'plugin'        : String,
                'plugin_check'  : String,
                'repeat'        : Integer,
                'repeat_on_error' : Integer,
                'check_infos'   : {
                    @key :  {
                        'key'       : String,
                        'cinfo_id'  : Integer,
                        'chk_id'    : Integer,
                        'value'     : String},
                },
                'groups' : {
                    'grp_id': {
                        'grp_id': Integer,
                        'name': String,
                    }, ...
                }
            },
        },
        'groups' :  {
            @grp_id : {
                'grp_id' : Integer,
                'name'   : String },
        },
        'objects':  {
            @obj_id : {
                'obj_id'        : Integer,
                'address'       : String,
                'creation_date' : datetime.date,
                'object_infos'   : {
                    @key :  {
                        'key'       : String,
                        'oinfo_id'  : Integer,
                        'obj_id'    : Integer,
                        'value'     : String},
                },

            },
        },
        'status': {
                [
                        'cg_id'         : Integer,
                        'chk_id'        : Integer,
                        'grp_id'        : Integer,
                        'obj_id'        : Integer,
                        'seq_id'        : Integer,
                        'check_message' : String,
                        'check_status'  : String,
                        'last_check'    : datetime.datetime,
                        'next_check'    : datetime.datetime,
                        'status_acknowledged_date': datetime.datetime
                        'status_changed_date': datetime.datetime,
                        'status_id': Integer,
                        'status_infos': {
                            @key :  {
                                'key'       : String,
                                'sinfo_id'  : Integer,
                                'status_id' : Integer,
                                'value'     : String},
                        },
                    },
        ]
    }
    """
    ret = get_status(_request, params)

    # Reorganize ret['@categorie'][@id][@key] to match old behavior ('get_detailed_infos' : False)
    if not params.get('get_detailed_infos', True):
        for categorie in ret:
            for _id in ret[categorie]:
                for cat_infos in ('object_infos', 'check_infos', 'status_infos'):
                    if cat_infos in ret[categorie][_id]:
                        for key in ret[categorie][_id][cat_infos]:
                            ret[categorie][_id][cat_infos][key] = ret[categorie][_id][cat_infos][key]['value']

    # Reorganize status to match with docstring
    ret_status_list = []
    for status_id in ret['status']:
        ret_status_list.append(ret['status'][status_id])
    ret['status'] = ret_status_list
    return ret

def _get_infos(pg_manager, ctx_list, query, ret, defaultparams=None, which_categorie='status'):
    """ Returns ret containing '@which_categorie'_infos from the supervision database filtered by @params """
    if which_categorie == 'status':
        fields = STATUS_INFOS_FIELDS
    elif which_categorie == 'objects':
        fields = OBJECT_INFOS_FIELDS
    elif which_categorie == 'checks':
        fields = CHECK_INFOS_FIELDS
    categorie_infos = (which_categorie == 'status' and which_categorie or which_categorie[:-1]) + "_infos"

    # Initialize categorie_infos
    for _id, categorie in ret[which_categorie].iteritems():
        if not categorie_infos in categorie:
            categorie[categorie_infos] = {}

    pg_manager.execute(ctx_list[0], query, defaultparams)
    for categorie_info in pg_manager.fetchall(ctx_list[0]):
        categorie_info_record = dict(zip((fields[0].split('.')[1], fields[1].split('.')[1], fields[2].split('.')[1],
                                          fields[3].split('.')[1]), categorie_info))
        _id = [v for k, v in categorie_info_record.iteritems() if k in ('obj_id', 'chk_id', 'status_id')][0]
        if _id in ret[which_categorie]:
            ret[which_categorie][_id][categorie_infos][categorie_info_record['key']] = categorie_info_record
    return ret

def _gen_query(query_from, query_where, which_categorie='status'):
    """ Returns query to get '@which_categorie'_infos """
    if which_categorie == 'status':
        fields = STATUS_INFOS_FIELDS
    elif which_categorie == 'objects':
        fields = OBJECT_INFOS_FIELDS
    elif which_categorie == 'checks':
        fields = CHECK_INFOS_FIELDS
    categorie_infos_id = (which_categorie == 'status' and 'status_id' or fields[1])
    query = "SELECT %s" % (', '.join([field for field in fields]))
    query += """ FROM %(db_infos)s
                WHERE %(categorie_infos_id)s
                IN (SELECT %(which_categorie)s.%(categorie_id)s %(query_from)s %(query_where)s)""" % ({
                                        'db_infos' : fields[0].split('.')[0],
                                        'categorie_infos_id' : categorie_infos_id,
                                        'which_categorie' : which_categorie,
                                        'categorie_id' : fields[1].split('.')[1],
                                        'query_from' : query_from,
                                        'query_where' : query_where})
    return query

def _get_queries_and_result_rows(pg_manager, ctx_list, defaultparams):
    """ Returns respectively rows result, query_from, query_where """
    where = []
    query_where = ""

    query_select    = "SELECT "  + ', '.join(STATUS_FIELDS + GROUP_FIELDS + CHECK_FIELDS + OBJECT_FIELDS) + " "
    query_from      = """FROM checks NATURAL
                         JOIN checks_group
                         NATURAL JOIN status
                         NATURAL JOIN objects_group
                         NATURAL JOIN objects
                         LEFT JOIN groups ON (groups.grp_id=objects_group.grp_id) """

    if defaultparams.get('object_address'):
        defaultparams['object_address'] = "%" + defaultparams['object_address'] + "%"
        where += ["objects.address ILIKE %(object_address)s"]

    # We map some defaultparams' values in db_mapping with a different key
    # in order to have keys with identic names than the database fields
    db_mapping = {}
    db_mapping['grp_id'] = defaultparams['group_id']
    db_mapping['name'] = defaultparams['group_name']
    db_mapping['chk_id'] = defaultparams['check_id']
    db_mapping['plugin'] = defaultparams['plugin_name']
    db_mapping['plugin_check'] = defaultparams['plugin_check']
    db_mapping['status_id'] = defaultparams['status_id']
    db_mapping['check_status'] = defaultparams['status']

    for key, value in db_mapping.items():
        if value and value is not True:
            for field in GROUP_FIELDS + CHECK_FIELDS + STATUS_FIELDS:
                if field.split('.')[1] == key:
                    if hasattr(value, '__iter__'):
                        ids = dict(zip(range(0, len(value)), value))
                        query_item = []
                        for key, value in ids.iteritems():
                            query_item.append('%%(__table_key_%s_%d__)s' % (field, key))
                            defaultparams.update({'__table_key_%s_%d__' % (field, key): value})
                        where += [field + " IN (%s)" % (', '.join(query_item))]
                        break
                    else:
                        where += [field + "=%(" + [key for key, v in defaultparams.iteritems() if v == value][0] + ")s"]
                        break

    if where:
        query_where = " WHERE " + " AND ".join(where)

    query_where += " ORDER BY status.next_check"

    if defaultparams.get('limit'):
        query_where += " LIMIT %d" % defaultparams['limit']

    pg_manager.execute(ctx_list[0], query_select + query_from + query_where, defaultparams)
    return pg_manager.fetchall(ctx_list[0]), query_from, query_where

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def get_status(pg_manager, ctx_list, _request, params=None):
    """ Returns checks, groups and objects from supervision database.

    @params: dictionary with parameters allowing fine grained selection of items from the SPV database
             paramaters can be one of the following:
        'status' (String or String List) get checks with the given status
        'group_name' (String or String List) name(s) of the group(s) to get checks for
        'object_address' (String) address of the object to get
        'plugin_name' (String) name of the plugin to get checks for
        'plugin_check' (String) name of the check to get
        'group_id' (Integer or Integer List) return group(s) whose id(s) is(are) the one(s) specified
        'check_id' (Integer) return check whose id is check_id
        'status_id' (Integer) return status whose id is status_id
        'limit' (Integer) maximum number of checks to get
        'get_status_infos' (Boolean, default False) get additional informations attached to the requested status
        'get_object_infos' (Boolean, default False) get additional informations attached to the requested objects
        'get_check_infos' (Boolean, default False) get additional informations attached to the request checks
        'get_check_groups' (Boolean, default False) get per check groups
        'next_check_expired' (Boolean, default False) require check that are new
        'update_next_check' (Boolean, default False) schedule next iteration of the checks
    @returns: a dictionary containing list of status, groups and objects
    {
        'checks': {
            @chk_id: {
                'chk_id'        : Integer,
                'name'          : String,
                'plugin'        : String,
                'plugin_check'  : String,
                'repeat'        : Integer,
                'repeat_on_error' : Integer,
                'check_infos'   : {
                    @key :  {
                        'key'       : String,
                        'cinfo_id'  : Integer,
                        'chk_id'    : Integer,
                        'value'     : String},
                },
                'groups' : {
                    'grp_id: {
                        'grp_id': Integer,
                        'name': String,
                    }, ...
                }
            },
        },
        'groups' :  {
            @grp_id : {
                'grp_id' : Integer,
                'name'   : String },
        },
        'objects':  {
            @obj_id : {
                'obj_id'        : Integer,
                'address'       : String,
                'creation_date' : datetime.date,
                'object_infos'   : {
                    @key :  {
                        'key'       : String,
                        'oinfo_id'  : Integer,
                        'obj_id'    : Integer,
                        'value'     : String},
                },

            },
        },
        'status': {
            @status_id {
                        'cg_id'         : Integer,
                        'chk_id'        : Integer,
                        'grp_id'        : Integer,
                        'obj_id'        : Integer,
                        'seq_id'        : Integer,
                        'check_message' : String,
                        'check_status'  : String,
                        'last_check'    : datetime.datetime,
                        'next_check'    : datetime.datetime,
                        'status_acknowledged_date': datetime.datetime
                        'status_changed_date': datetime.datetime,
                        'status_id': Integer,
                        'status_infos': {
                            @key :  {
                                'key'       : String,
                                'sinfo_id'  : Integer,
                                'status_id' : Integer,
                                'value'     : String},
                        },
                    },
        }
    }
    """

    defaultparams = {
        'status'            : None,
        'group_name'        : None,
        'object_address'    : None,
        'plugin_name'       : None,
        'plugin_check'      : None,
        'group_id'          : None,
        'check_id'          : None,
        'status_id'         : None,
        'limit'             : None,
        'get_status_infos'  : False,
        'get_object_infos'  : False,
        'get_check_infos'   : False,
        'get_check_groups'  : False,
        'next_check_expired': False,
        'update_next_check' : False
    }

    if params:
        defaultparams.update(params)

    ret = {'objects' : {}, 'checks' : {}, 'groups' : {}, 'status' : {}}

    rows, query_from, query_where = _get_queries_and_result_rows(pg_manager, ctx_list, defaultparams)

    statuss = reduce(lambda dicts, row: dicts + [dict(zip(STATUS_FIELDS + GROUP_FIELDS + CHECK_FIELDS + OBJECT_FIELDS, row))], rows, [])
    for spvstatus in statuss:
        group  = dict(reduce(lambda pairs, key: pairs + ((key[len('groups.'):],  spvstatus[key]),), GROUP_FIELDS,  ()))
        stat   = dict(reduce(lambda pairs, key: pairs + ((key[len('status.'):],  spvstatus[key]),), STATUS_FIELDS, ()))
        check  = dict(reduce(lambda pairs, key: pairs + ((key[len('checks.'):],  spvstatus[key]),), CHECK_FIELDS,  ()))
        obj    = dict(reduce(lambda pairs, key: pairs + ((key[len('objects.'):], spvstatus[key]),), OBJECT_FIELDS, ()))

        ret['groups'].setdefault(group['grp_id'], group)
        ret['checks'].setdefault(check['chk_id'], check)
        ret['objects'].setdefault(obj['obj_id'], obj)
        ret['status'].setdefault(stat['status_id'], stat)

        stat['status_id'] = spvstatus['status.status_id']
        stat['grp_id'] = spvstatus['groups.grp_id']
        stat['obj_id'] = spvstatus['objects.obj_id']
        stat['chk_id'] = spvstatus['checks.chk_id']

        if defaultparams.get('get_check_groups'):
            if not 'groups' in ret['checks'][check['chk_id']]:
                ret['checks'][check['chk_id']]['groups'] = {}
            ret['checks'][check['chk_id']]['groups'][group['grp_id']] = group

    if defaultparams.get('get_status_infos'):
        query = _gen_query(query_from, query_where, 'status')
        ret = _get_infos(pg_manager, ctx_list, query, ret, defaultparams)

    if defaultparams.get('get_object_infos'):
        query = _gen_query(query_from, query_where, 'objects')
        ret = _get_infos(pg_manager, ctx_list, query, ret, defaultparams, 'objects')

    if defaultparams.get('get_check_infos'):
        query = _gen_query(query_from, query_where, 'checks')
        ret = _get_infos(pg_manager, ctx_list, query, ret, defaultparams, 'checks')

    if defaultparams['update_next_check']:
        for status in ret['status'].values():
            pg_manager.execute(ctx_list[0],
                    "UPDATE status SET next_check=now() + CAST ('%(repeat)s seconds' AS INTERVAL) " \
                    "WHERE status_id=%(status_id)s AND seq_id=%(seq_id)s",
                    {'status_id' : status['status_id'], 'repeat' : ret['checks'][status['chk_id']]['repeat'], 'seq_id' : status['seq_id']})

    pg_manager.commit(ctx_list[0])
    return ret

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def get_plugin_checks(pg_manager, ctx_list, _request, params=None):
    """ Returns checks from the supervision database filtered by @params.

    @params: dictionary of filters to apply to get checks
        'plugin_name' (String)
        'plugin_check_name' (String)
        'check_id' (Integer)
        'info_key' (String)
        'info_value' (String)
    @returns: list of checks
        [{
            'chk_id': Integer,
            'plugin': String,
            'plugin_check': String,
            'name': String,
            'repeat': Integer,
            'repeat_on_error': Integer
        }, { }, ... ]
    """

    defaultparams  = {
        'plugin_name'       : None,
        'plugin_check_name' : None,
        'check_id'          : None,
        'info_key'         : None,
        'info_value'       : None
    }

    if params:
        defaultparams.update(params)

    where = []
    query  = "SELECT chk_id, plugin, plugin_check, name, repeat, repeat_on_error FROM checks"
    if defaultparams['plugin_name']:       where += ["plugin=%(plugin_name)s"]
    if defaultparams['plugin_check_name']: where += ["plugin_check=%(plugin_check_name)s"]
    if defaultparams['check_id']:          where += ["chk_id=%(check_id)s"]
    if defaultparams['info_key']:         where += ["key=%(info_key)s"]
    if defaultparams['info_value']:       where += ["value=%(info_value)s"]

    if defaultparams['info_value'] or defaultparams['info_key']:
        query += " NATURAL JOIN check_infos "
    if where:             query += " WHERE " + " AND ".join(where)

    pg_manager.execute(ctx_list[0], query, defaultparams)
    rows = pg_manager.fetchall(ctx_list[0])
    checks = {}
    for row in rows:
        checks[row[0]] = dict(zip(("chk_id", "plugin", "plugin_check", "name", "repeat", "repeat_on_error"), row))

    return checks


def _get_groups(pg_manager, ctx_list, _request, params=None):
    """ Returns groups from the supervision database filtered by @params

    @params: dictionary of filters to apply to get groups
        'group_id' (Integer)
        'group_name' (String)
        'get_objects' (Boolean, default False)
    @returns: list of groups
        [{
            'id': Integer,
            'name': String
            'objects': {
                @obj_id: {
                    @obj_id: Integer,
                    address: String,
                    creation_date: database.date
                }, ...
            }
        }, ... ]
    """

    defaultparams = {
        'group_name': None,
        'group_id'  : None,
        'get_objects': False,
    }

    if params:
        defaultparams.update(params)

    where = []
    query  = "SELECT grp_id, name FROM groups"
    if defaultparams['group_name']: where += ["name=%(group_name)s"]
    if defaultparams['group_id']:   where += ["grp_id=%(group_id)s"]
    if where:      query += " WHERE " + " AND ".join(where)

    pg_manager.execute(ctx_list[0], query, defaultparams)
    rows = pg_manager.fetchall(ctx_list[0])
    groups = {}
    for row in rows:
        groups[row[0]] = {"id" : row[0], "name" : row[1]}
        if defaultparams.get('get_objects'):
            groups[row[0]]['objects'] = {}
            query = """ SELECT o.obj_id, o.address, o.creation_date
                        FROM objects_group ob JOIN objects o ON (ob.obj_id = o.obj_id)
                        WHERE ob.grp_id = %s"""
            pg_manager.execute(ctx_list[0], query, [row[0]])
            objs = pg_manager.fetchall(ctx_list[0])
            for obj in objs:
                groups[row[0]]['objects'][obj[0]] = {'obj_id': obj[0], 'address': obj[1], 'creation_date': obj[2]}
            if not groups[row[0]]['objects']:
                del groups[row[0]]['objects']

    return groups


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def get_groups(pg_manager, ctx_list, _request, params=None):
    """ Returns groups from the supervision database filtered by @params

    @params: dictionary of filters to apply to get groups
        'group_id' (Integer)
        'group_name' (String)
    @returns: list of groups
        [{
            'id': Integer,
            'name': String,
            'objects': {
                @obj_id: {
                    @obj_id: Integer,
                    address: String,
                    creation_date: database.date
                }, ...
            }
        }, ... ]
    """
    return _get_groups(pg_manager, ctx_list, _request, params)


def _get_objects(pg_manager, ctx_list, _request, params=None):
    """ Returns objects from the supervision database filtered by @params

    @params: dictionary of filters to apply to get groups
        'obj_id' (Integer)
        'address' (String)
        'creation_date' (String)
        'info_key' (String)
        'info_value' (String)
        'get_object_groups' (Boolean, default False) get per object groups
    @returns: list of objects
        [{
            'obj_id': Integer,
            'address': String,
            'creation_date': database.date
            'groups': {
                'grp_id': {
                    grp_id: Integer,
                    name: String,
                }, ...
            }
        }, ... ]
    """

    defaultparams = {
        'obj_id'        : None,
        'address'       : None,
        'creation_date' : None,
        'info_key'      : None,
        'info_value'    : None,
        'get_object_groups': False,
    }

    if params:
        defaultparams.update(params)

    where = []

    query_fields = []
    query_fields += OBJECT_FIELDS
    if defaultparams['get_object_groups']:
        query_fields += GROUP_FIELDS

    query  = "SELECT " + ",".join(query_fields) + " FROM objects"
    if defaultparams['obj_id']: where += ["objects.obj_id=%(obj_id)s"]
    if defaultparams['address']: where += ["objects.address=%(address)s"]
    if defaultparams['creation_date']:   where += ["objects.creation_date=%(creation_date)s"]
    if defaultparams['info_key']:         where += ["object_infos.key=%(info_key)s"]
    if defaultparams['info_value']:       where += ["object_infos.value=%(info_value)s"]

    if defaultparams['info_key'] or defaultparams['info_value']:
        query += " JOIN object_infos ON object_infos.obj_id = objects.obj_id "
    if defaultparams['get_object_groups']:
        query += " LEFT JOIN objects_group ON (objects.obj_id = objects_group.obj_id) "
        query += " LEFT JOIN groups ON (objects_group.grp_id = groups.grp_id) "
    if where:      query += " WHERE " + " AND ".join(where)

    pg_manager.execute(ctx_list[0], query, defaultparams)
    rows = pg_manager.fetchall(ctx_list[0])
    objects = {}
    for row in rows:
        objects[row[0]] = {"obj_id" : row[0], "address" : row[1], "creation_date" : row[2]}
        if defaultparams['get_object_groups']:
            if not 'groups' in objects[row[0]]:
                objects[row[0]]['groups'] = {}
            if not row[3] is None and not row[4] is None:
                objects[row[0]]['groups'][row[3]] = {'grp_id': row[3], 'name': row[4]}

    return objects


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def get_objects(pg_manager, ctx_list, _request, params=None):
    """ Returns objects from the supervision database filtered by @params

    @params: dictionary of filters to apply to get objects
        'obj_id' (Integer)
        'address' (String)
        'creation_date' (String)
        'info_key' (String)
        'info_value' (String)
        'get_object_groups' (Boolean, default False) get per object groups
    @returns: list of objects
        [{
            'obj_id': Integer,
            'address': String,
            'creation_date': database.date
            'groups': {
                'grp_id': {
                    grp_id: Integer,
                    name: String,
                }, ...
            }
        }, ... ]
    """
    return _get_objects(pg_manager, ctx_list, _request, params)


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def acknowledge_status(pg_manager, ctx_list, _request, status_id):
    """ Acknowledge status for @status_id check. """

    query  = "UPDATE status SET status_acknowledged_date=now() WHERE status_id=%(status_id)s"
    pg_manager.execute(ctx_list[0], query, {"status_id" : status_id})
    pg_manager.commit(ctx_list[0])

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def reschedule_check(pg_manager, ctx_list, _request, status_id):
    """ Reschedule check immediately for @status_id check. """

    if hasattr(status_id, '__iter__'):
        query = "UPDATE status SET next_check=now() WHERE status_id IN %(status_id)s"
    else:
        query = "UPDATE status SET next_check=now() WHERE status_id=%(status_id)s"
    pg_manager.execute(ctx_list[0], query, {'status_id' : hasattr(status_id, '__iter__') and tuple(status_id) or status_id})
    pg_manager.commit(ctx_list[0])

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def set_checks_status(pg_manager, ctx_list, _request, checks):
    """ Sets results of provided @checks.

    @checks: must be a list of check dictionaries of the form
        [{'status_id': sts_id_value,
         'sequence_id': seq_id_value,
         'status': sts_value,
         'message': msg_value,
         'status_infos': infos_dict,
         }, ... ]
    """

    for check in checks:
        if check['status_id'] == None:
            logger.error('set_checks_status: Trying to set check status with invalid input parameter (status_id): %s' % (str(check)))
            continue

        query = """SELECT repeat, repeat_on_error FROM spv.status NATURAL JOIN spv.checks_group NATURAL JOIN spv.checks WHERE status_id=%(status_id)s"""
        pg_manager.execute(ctx_list[0], query, check)
        res  = pg_manager.fetchone(ctx_list[0])
        if not res:
            logger.error('status_id %s does not exist anymore. Skipping status update' % (str(check)))
            continue
        repeat, repeat_on_error = res


        if check['status'] == 'ERROR':
            set_next_check = """, next_check = next_check
                                             - CAST ('%s seconds' AS INTERVAL)
                                             + CAST ('%s seconds' AS INTERVAL)""" % (repeat, repeat_on_error)
        else:
            set_next_check = ""
        query  = """UPDATE status SET last_check=now(), check_status=%(status)s, check_message=%(message)s, seq_id = seq_id + 1"""
        query += set_next_check
        query += """ WHERE status_id=%(status_id)s AND seq_id=%(sequence_id)s"""
        pg_manager.execute(ctx_list[0], query, check)
        if check.get('status_infos'):
            tmp_dict = sjutils.flatten_dict(check['status_infos'], sep = ':')
            for key, value in tmp_dict.iteritems():
                query = """INSERT INTO status_infos_view (status_id, key, value) VALUES (%(status_id)s, %(key)s, %(value)s)"""
                pg_manager.execute(ctx_list[0], query, {'status_id': check['status_id'],
                                     'key': str(key),
                                     'value': str(value)})

    pg_manager.commit(ctx_list[0])

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def create_objects(pg_manager, ctx_list, _request, objects):
    """ Create new objects with provided data.

    @checks: must be a list of object dictionaries of the form:
        [{
            'address': String,
            'group_id': Integer (optional),
            'infos': (optional) {
                @key: @value,
                ...
            }
        }, ... ]
        For each check, it is possible to automatically add it to an existing group according to its @group_id.
    @returns: dictionary containing new objects and if an error occurs during object creation, it is appended
              to the @errors key with an added @message key containing the error message. All changes related to the
              failed object creation will be rolled back.
        {
            'errors': [{
                @object-keys: @object-values,
                'message': String
                }, ... ],
            @obj_id: {
                'obj_id': Integer,
                'address': String,
                'creation_date': datetime.date
            }, ...
        }
    """

    ret = {}
    errors = []
    db_obj = None
    savepoint = 0
    for obj in objects:
        try:
            savepoint += 1
            db_obj = None
            # Insert object
            pg_manager.execute(ctx_list[0], "SAVEPOINT save%s" % savepoint)
            query = "INSERT INTO objects (address) VALUES (%(obj_address)s) RETURNING obj_id, address, creation_date"
            pg_manager.execute(ctx_list[0], query, {'obj_address': obj['address']})
            db_obj = pg_manager.fetchall(ctx_list[0])[0]
            ret[db_obj[0]] = {'obj_id': db_obj[0], 'address': db_obj[1], 'creation_date': db_obj[2]}

            # Insert object_infos
            if 'infos' in obj:
                for key, value in obj['infos'].iteritems():
                    query = """INSERT INTO object_infos (obj_id, key, value) VALUES
                        (%(obj_id)s, %(obj_key)s, %(obj_value)s)"""
                    pg_manager.execute(ctx_list[0], query,
                        {'obj_id': db_obj[0], 'obj_key': key, 'obj_value': value})

            # Assign to existing group
            if 'group_id' in obj:
                query = "INSERT INTO objects_group (obj_id, grp_id) VALUES (%(obj_id)s, %(group_id)s)"
                pg_manager.execute(ctx_list[0], query, {'obj_id': db_obj[0], 'group_id': obj['group_id']})

        except sjutils.PgConnManager.DatabaseError, error:
            logger.debug('Rollback object creation for address %s.' % obj['address'])
            pg_manager.execute(ctx_list[0], "ROLLBACK TO save%s" % savepoint)
            if db_obj:
                del ret[db_obj[0]]
            obj['message'] = str(error)
            errors.append(obj)

    pg_manager.commit(ctx_list[0])
    if errors:
        ret['errors'] = errors

    return ret

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def create_checks(pg_manager, ctx_list, _request, checks):
    """ Create new checks with provided data.

    @checks: must be a list of check dictionaries of the form:
        [{
            'plugin': String,
            'plugin_check': String,
            'name': String,
            'repeat': Integer,
            'repeat_on_error': Integer,
            'group_id': Integer (optional),
            'infos': (optional) {
                @key: @value,
                ...
            }
        }, ... ]
        For each check, it is possible to automatically add it to an existing group according to its @group_id.
    @returns: dictionary containing new checks and if an error occurs during object creation, it is appended
              to the @errors key with an added @message key containing the error message. All changes related to the
              failed check creation will be rolled back.
        {
            'errors': [{
                @object-keys: @object-values,
                'message': String
                }, ... ],
            @chk_id: {
                'chk_id': Integer,
                'plugin': String,
                'plugin_check': String,
            }, ...
        }
    """

    ret = {}
    errors = []
    db_chk = None
    savepoint = 0
    for chk in checks:
        try:
            # Insert check
            savepoint += 1
            db_chk = None
            pg_manager.execute(ctx_list[0], "SAVEPOINT save%s" % savepoint)
            query = """INSERT INTO checks (plugin, plugin_check, name, repeat, repeat_on_error)
                VALUES (%(plugin)s, %(plugin_check)s, %(name)s, %(repeat)s, %(repeat_on_error)s) RETURNING chk_id, plugin, plugin_check"""
            pg_manager.execute(ctx_list[0], query, {
                'plugin': chk['plugin'],
                'plugin_check': chk['plugin_check'],
                'name': chk['name'],
                'repeat': chk['repeat'],
                'repeat_on_error': chk['repeat_on_error']
            })
            db_chk = pg_manager.fetchall(ctx_list[0])[0]

            ret[db_chk[0]] = {'chk_id': db_chk[0], 'plugin': db_chk[1], 'plugin_check': db_chk[2]}

            # Insert check_infos
            if 'infos' in chk:
                for key, value in chk['infos'].iteritems():
                    query = """INSERT INTO check_infos (chk_id, key, value) VALUES
                        (%(chk_id)s, %(chk_key)s, %(chk_value)s)"""
                    pg_manager.execute(ctx_list[0], query,
                        {'chk_id': db_chk[0], 'chk_key': key, 'chk_value': value})

            # Assign to existing group
            if 'group_id' in chk:
                query = "INSERT INTO checks_group (chk_id, grp_id) VALUES (%(chk_id)s, %(group_id)s)"
                pg_manager.execute(ctx_list[0], query, {'chk_id': db_chk[0], 'group_id': chk['group_id']})

        except sjutils.PgConnManager.DatabaseError, error:
            logger.debug('Rollback check creation for %s.%s.' % (chk['plugin'], chk['plugin_check']))
            pg_manager.execute(ctx_list[0], "ROLLBACK TO save%s" % savepoint)
            if db_chk:
                del ret[db_chk[0]]
            chk['message'] = str(error)
            errors.append(chk)
    pg_manager.commit(ctx_list[0])

    if errors:
        ret['errors'] = errors

    return ret

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def create_groups(pg_manager, ctx_list, _request, groups):
    """ Create new groups.

    @groups: list of group names
        [String, String, ...]
    @returns: dictionary containing new groups and if an error occurs during object creation, it is appended
              to the @errors key with an added @message key containing the error message. All changes related to the
              failed group creation will be rolled back.
        {
            'errors': [{
                @object-keys: @object-values,
                'message': String
                }, ... ],
            @group_id: {
                'grp_id': Integer,
                'name': String
            }, ...
        }
    """

    ret = {}
    errors = []
    db_grp = None
    savepoint = 0
    for grp in groups:
        try:
            # Insert check
            savepoint += 1
            pg_manager.execute(ctx_list[0], "SAVEPOINT save%s" % savepoint)
            query = """INSERT INTO groups (name)
                VALUES (%(name)s) RETURNING grp_id, name"""
            pg_manager.execute(ctx_list[0], query, {'name': grp})
            db_grp = pg_manager.fetchall(ctx_list[0])[0]

            ret[db_grp[0]] = {'grp_id': db_grp[0], 'name': db_grp[1]}

            pg_manager.commit(ctx_list[0])
        except sjutils.PgConnManager.DatabaseError, error:
            logger.debug('Rollback group creation for %s.' % grp['name'])
            pg_manager.execute(ctx_list[0], "ROLLBACK TO save%s" % savepoint)
            if db_grp:
                del ret[db_grp[0]]
            grp['message'] = str(error)
            errors.append(grp)

    if errors:
        ret['errors'] = errors

    return ret

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def delete_objects(pg_manager, ctx_list, _request, object_ids):
    """ Delete a set of objects.

    Will raise an error and rollback all deletions if an error occurs.

    @object_ids: a list of object ids
        [ Integer, Integer, ... ]
    """

    __delete_item(pg_manager, ctx_list, 'objects', 'obj_id', object_ids)

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def delete_checks(pg_manager, ctx_list, _request, check_ids):
    """ Delete a set of checks.

    Will raise an error and rollback all deletions if an error occurs.

    @check_ids: a list of check ids
        [ Integer, Integer, ... ]
    @see: delete_objects
    """

    __delete_item(pg_manager, ctx_list, 'checks', 'chk_id', check_ids)

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def delete_groups(pg_manager, ctx_list, _request, group_ids):
    """ Delete a set of groups.

    Will raise an error and rollback all deletions if an error occurs.

    @group_ids: a list of group ids
        [ Integer, Integer, ... ]
    @see: delete_objects
    """

    __delete_item(pg_manager, ctx_list, 'groups', 'grp_id', group_ids)

@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def delete_status_infos(pg_manager, ctx_list, _request, sinfo_ids):
    """ Delete a set of status infos.

    Will raise an error and rollback all deletions if an error occurs.

    @sinfo_ids: a list of sinfo ids
        [ Integer, Integer, ... ]
    @see: delete_objects
    """

    __delete_item(pg_manager, ctx_list, 'status_infos', 'sinfo_id', sinfo_ids)

def __delete_item(pg_manager, ctx_list, table, table_key, item_list):
    """ Delete a set of items from @table. """

    ids = dict(zip(range(0, len(item_list)), item_list))
    query_item = []
    query_dict = {}
    for key, value in ids.iteritems():
        query_item.append('%%(__table_key_%d__)s' % key)
        query_dict.update({'__table_key_%d__' % key: value})
    query_dict.update({'table': table, 'table_key': table_key})
    query = 'DELETE FROM %s WHERE %s IN (%s)' % (table, table_key, ','.join(query_item))

    try:
        pg_manager.execute(ctx_list[0], query, query_dict)
        pg_manager.commit(ctx_list[0])
    except sjutils.PgConnManager.DatabaseError, _error:
        logger.debug('Rollback delete in table %s' % table)
        raise

def __update_infos(pg_manager, ctx_list, table_infos, item_infos):
    """ Generate SQL queries to update/delete infos.

    @table_infos: dictionary
        {
            'table_name': String,
            'table_id': String,
            'table_id_value': Integer
        }
    @item_infos: dictionary
        {
            'insert': { @key: String, ... }
            'delete': { @key: String, ... }
        }
    """

    if 'insert' in item_infos:
        for key, value in item_infos['insert'].iteritems():
            query = """INSERT INTO %(table_name)s
                (%(table_id)s, key, value) VALUES (%(table_id_value)s, %%(key)s, %%(value)s)""" % table_infos
            pg_manager.execute(ctx_list[0], query, {'key': key, 'value': value})

    if 'delete' in item_infos:
        for key, value in item_infos['delete'].iteritems():
            query = """DELETE FROM %(table_name)s WHERE %(table_id)s=%(table_id_value)s
                AND (key=%%(key)s OR value=%%(value)s)""" % table_infos
            pg_manager.execute(ctx_list[0], query, {'key': key, 'value': value})


def _group_manage_objects(pg_manager, ctx_list, action, group, objects):
    """  Add/remove a list of objects to/from a specified group according to action

    Action could be add or remove.
    """

    infos = {'errors': []}

    if not action in ('add', 'remove'):
        raise ValueError('Unknown action %s' % action)

    grp_id = 0
    if isinstance(group, int):
        grps = _get_groups(pg_manager, ctx_list, None, {'group_id': group})
        if not len(grps) > 0:
            infos['errors'].append({'type': 'group', 'grp_id': group, 'message': 'Not found in database'})
            return infos
        grp_id = group
    elif isinstance(group, str):
        grps = _get_groups(pg_manager, ctx_list, None, {'name': group})
        if not len(grps) > 0:
            infos['errors'].append({'type': 'group', 'name': group, 'message': 'Not found in database'})
            return infos
        grp_id = grps.keys()[0]
    else:
        raise TypeError('group expecting to be an integer or a string')

    # Determine list type according to first element.
    if len(objects) > 0:
        list_type = 'int'
        obj = objects[0]
        if isinstance(obj, int):
            list_type = 'int'
        elif isinstance(obj, str):
            list_type = 'str'
        else:
            raise TypeError('Obj expecting to be an integer or a string')

    for obj in objects:
        obj_id = 0
        if list_type == 'int':
            objs = _get_objects(pg_manager, ctx_list, None, {'obj_id': obj})
            if not len(objs) > 0:
                infos['errors'].append({'type': 'object', 'obj_id': obj, 'message': 'Not found in database'})
                continue
            obj_id = obj
        elif list_type == 'str':
            objs = _get_objects(pg_manager, ctx_list, None, {'address': obj})
            if not len(objs) > 0:
                infos['errors'].append({'type': 'object', 'address': obj, 'message': 'Not found in database'})
                continue
            obj_id = objs.keys()[0]
        else:
            raise TypeError('Obj expecting to be an integer or a string')

        query = ''
        if action == 'add':
            query = 'INSERT INTO objects_group (grp_id, obj_id) VALUES (%s, %s)'

        elif action == 'remove':
            query = 'DELETE FROM objects_group WHERE grp_id = %s AND obj_id = %s'

        else:
            break

        try:
            pg_manager.execute(ctx_list[0], query, (grp_id, obj_id))
        except sjutils.PgConnManager.DatabaseError, error:
            infos['errors'].append({'type': 'objects_group', 'obj_id': obj_id, 'grp_id': grp_id, 'message': str(error)})

    pg_manager.commit(ctx_list[0])

    if len(infos['errors']) == 0:
        del infos['errors']

    return infos


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def group_add_objects(pg_manager, ctx_list, _request, params):
    """ Add a list of objects to a specified group according to @params.

    Group and objects could be specified using their ids or unique string identifier.

    @params: dictionary of the form:
        {
            'group': Integer or String,
            'objects' : [ Integer or String, ... ]
        }
    @returns: dictionary containing a list of errors.
        {
            'errors': [{
                'type': String,
                @object-key: @object-value,
                'message': String
                }, ... ]
        }
    """
    return _group_manage_objects(pg_manager, ctx_list, 'add', params['group'], params['objects'])


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def group_remove_objects(pg_manager, ctx_list, _request, params):
    """ Remove a list of objects from a specified group according to @params.

    Group and objects could be specified using their ids or unique string identifier.

    @params: dictionary of the form:
        {
            'group': Integer or String,
            'objects' : [ Integer or String, ... ]
        }
    @returns: dictionary containing a list of errors.
        {
            'errors': [{
                'type': String,
                @object-key: @object-value,
                'message': String
                }, ... ]
        }
    """
    return _group_manage_objects(pg_manager, ctx_list, 'remove', params['group'], params['objects'])


@exportable
@webengine_pgconn('/etc/webengine/webengine-spv.conf')
def update(pg_manager, ctx_list, _request, params):
    """ Update checks, groups and objects according to @params.

    If an error occurs during the update, the method will raise an error and rollback all changes.

    @params: dictionary of the form:
        {
            'objects':  {
                @obj_id : {
                    'obj_id'        : Integer,
                    'address'       : String,
                    'infos'         : {
                        'insert': { @key : String, ... },
                        'delete': { @key : String, ... }
                    }
                }, ...
            },
            'checks': {
                @chk_id: {
                    'chk_id'        : Integer,
                    'name'          : String,
                    'plugin'        : String,
                    'plugin_check'  : String,
                    'repeat'        : Integer,
                    'repeat_on_error' : Integer,
                    'infos'         : {
                        'insert': { @key : String, ... },
                        'delete': { @key : String, ... }
                    }
                }, ...
            },
            'groups' :  {
                @grp_id : {
                    'grp_id' : Integer,
                    'name'   : String
                }, ...
            }
        }
        Please note that chk_id, obj_id or grp_id are mandatory items that will not be changed.
    """

    try:
        # Update objects
        if 'objects' in params:
            for obj_id, obj_update in params['objects'].iteritems():
                query = "UPDATE objects SET address=%(address)s WHERE obj_id=%(obj_id)s"
                pg_manager.execute(ctx_list[0], query, obj_update)

                if 'infos' in obj_update:
                    __update_infos(pg_manager, ctx_list,
                        {'table_name': 'object_infos', 'table_id': 'obj_id', 'table_id_value': obj_id},
                        obj_update['infos'])

        # Update checks
        if 'checks' in params:
            for chk_id, chk_update in params['checks'].iteritems():
                for chk_param in ('name', 'plugin', 'plugin_check', 'repeat', 'repeat_on_error'):
                    query = "UPDATE checks SET " + chk_param + "=%(" + chk_param + ")s WHERE chk_id=%(chk_id)s"
                    pg_manager.execute(ctx_list[0], query, chk_update)

                if 'infos' in chk_update:
                    __update_infos(pg_manager, ctx_list,
                        {'table_name': 'check_infos', 'table_id': 'chk_id', 'table_id_value': chk_id},
                        chk_update['infos'])

        # Update groups
        if 'groups' in params:
            for _grp_id, grp_update in params['groups'].iteritems():
                query = "UPDATE groups SET name=%(name)s WHERE grp_id=%(grp_id)s"
                pg_manager.execute(ctx_list[0], query, grp_update)

        pg_manager.commit(ctx_list[0])
    except sjutils.PgConnManager.DatabaseError, _error:
        logger.debug('Rollback update')
        raise

