from django.contrib.auth.decorators import login_required
from webengine.utils.decorators import render
from webengine.spv.forms import SearchSupervisionForm
from webengine.spv import services
import datetime


def is_status_acknowledged(status):
    if status['check_status'] != 'FINISHED':
        if status['status_changed_date']:
            if status['status_acknowledged_date']:
                return status['status_acknowledged_date'] > status['status_changed_date']
            else:
                return False
    return True

def is_status_overdue(status, check):
    lastcheck_max_date = datetime.datetime.now() - datetime.timedelta(seconds=check['repeat']) - datetime.timedelta(minutes=1)
    check_due_date = status['next_check'] + datetime.timedelta(minutes=1)
    if status['last_check'] < lastcheck_max_date:
        return True
    if datetime.datetime.now() > check_due_date:
        if status['status_acknowledged_date']:
            return status['status_acknowledged_date'] < check_due_date
        else:
            return True
    return False


@login_required
@render(view='index')
def index(request, _sort=None, _column=None):

    search_address  = None
    search_status   = None
    search_group_id = None
    search_check_id = None

    groups = services.get_groups(request)
    checks = services.get_plugin_checks(request)

    ret = {'display' : 'STATUS', 'refresh' : False}

    if request.method == 'POST':
        form = SearchSupervisionForm(request, groups, checks, data=request.POST)
        if form.is_valid():
            search_address = form.cleaned_data['address']
            if not form.cleaned_data['status'] == 'ALL':
                search_status   = [form.cleaned_data['status']]
            if not form.cleaned_data['group'] == 'ALL':
                search_group_id = int(form.cleaned_data['group'])
            if not form.cleaned_data['check'] == 'ALL':
                search_check_id = int(form.cleaned_data['check'])
            if form.cleaned_data['refresh'].isdigit():
                ret['refresh'] = True
                ret['refresh_interval'] = str(int(form.cleaned_data['refresh']) * 1000)
            ret['display'] = form.cleaned_data['display']
    else:
        form = SearchSupervisionForm(request, groups, checks)
    ret['form'] = form

    status = services.get_checks(request, {'object_address' : search_address, 'group_id' : search_group_id, 'status' : search_status, 'check_id' :search_check_id})
    if ret['display'] == 'STATUS':
        ret['groups'] = create_status_dic(status)
    else:
        ret['status'] = create_history_dic(status)
    return ret

def create_history_dic(status_list):
    """ Builds an history dictionary for provided @status_list. """

    ret = []
    dates = {}
    for item in status_list['status']:
        entry = get_status_details(status_list, item)
        dates.setdefault(entry['status_changed_date_raw'], [])
        dates[entry['status_changed_date_raw']] += [entry]
    keys = dates.keys()
    keys.sort()
    keys.reverse()
    for key in keys:
        for st in dates[key]:
            ret += [st]
    return ret

def create_status_dic(status):
    ret = []
    groups = {}
    groups_checks = {}
    for st in status['status']:
        if st['grp_id'] not in groups:
            groups[st['grp_id']] = {'name' : st['grp_id'], 'id' : st['grp_id'], 'objects' : {} }

        groups[st['grp_id']]['objects'].setdefault(st['obj_id'], {})
        groups[st['grp_id']]['objects'][st['obj_id']][st['chk_id']] = st

        groups_checks.setdefault(st['grp_id'], [])
        st['acknowledged'] = is_status_acknowledged(st)
        st['overdue'] = is_status_overdue(st, status['checks'][st['chk_id']])
        if st['chk_id'] not in groups_checks[st['grp_id']]:
            groups_checks[st['grp_id']] += [st['chk_id']]

    for grp_id in groups_checks:
        group = {}
        group['id'] = grp_id
        group['name'] = status['groups'][grp_id]['name']
        group['objects'] = []
        group['checks'] = []
        for chk_id in groups_checks[grp_id]:
            group['checks'] += [{'id' : chk_id, 'plugin' : status['checks'][chk_id]['plugin'], 'check' : status['checks'][chk_id]['plugin_check']}]

        # Constructing a dict {'address' : obj_id, ....}
        all_objects = dict(reduce(lambda all_objects, obj_id: all_objects + [[status['objects'][obj_id]['address'], obj_id,]], groups[grp_id]['objects'].keys(), []))
        objects_addresses = all_objects.keys()
        # Sorting addresses alphabetically
        objects_addresses.sort(cmp=lambda x, y: x.lower() < y.lower() and -1 or 1)
        for address in objects_addresses:
            obj_id = all_objects[address]
            obj = {'obj_id' : obj_id, 'address' : status['objects'][obj_id]['address']}
            obj['expand'] = False
            obj['status'] = []
            for chk_id in groups_checks[grp_id]:
                if chk_id in groups[grp_id]['objects'][obj_id]:
                    obj['status'] += [groups[grp_id]['objects'][obj_id][chk_id]]
                else:
                    obj['status'] += [None]
            group['objects'] += [obj]
        ret += [group]

    return ret

@login_required
@render
def status_reschedule(request, status_id):
    services.reschedule_check(request, status_id=status_id)
    return "OK"

@login_required
@render
def status_acknowledge(request, status_id):
    services.acknowledge_status(request, status_id=status_id)
    return "OK"

@login_required
@render(view='statusdetails')
def status_details(request, status_id):
    """ Get status details for a given @status_id. """

    checks_data = services.get_checks(request, {'status_id' : status_id, 'get_status_infos' : True, "get_check_infos" : True, "get_object_infos" : True, "get_detailed_infos" : True})

    if not checks_data['status']:
        return {'retcode' : 'ko', 'retmsg' : 'Status does not exist'}

    ret = get_status_details(checks_data, checks_data['status'][0])
    ret['retcode'] = 'ok'

    return ret

def get_status_details(checks_data, status):
    """ Returns status details of a single @status in a pythonic, flattened dictionary. """

    check  = checks_data['checks'][status['chk_id']]
    group  = checks_data['groups'][status['grp_id']]
    obj    = checks_data['objects'][status['obj_id']]

    ret = {}
    ret['check_id']           = status['chk_id']
    ret['group_id']           = status['grp_id']
    ret['object_id']          = status['obj_id']
    ret['status_id']          = status['status_id']
    ret['check_status']       = status['check_status']

    ret['check_name']            = check['name']
    ret['check_plugin']          = check['plugin']
    ret['check_plugin_check']    = check['plugin_check']
    ret['check_repeat']          = check['repeat']
    ret['check_repeat_on_error'] = check['repeat_on_error']

    ret['group_name']            = group['name']

    ret['object_address']        = obj['address']
    ret['object_creation_date']  = obj['creation_date'].strftime("%D %H:%M:%S")

    ret['last_check']                = status['last_check'].strftime("%D %H:%M:%S")
    ret['next_check']                = status['next_check'].strftime("%D %H:%M:%S")
    ret['status_changed_date_raw']   = status['status_changed_date'] and status['status_changed_date'] or datetime.datetime(2009, 1, 12, 0, 0)
    ret['status_changed_date']       = status['status_changed_date'] and status['status_changed_date'].strftime("%D %H:%M:%S") or ''
    ret['status_acknowledged_date']  = status['status_acknowledged_date'] and status['status_acknowledged_date'].strftime("%D %H:%M:%S") or ''

    ret['check_message']     = status['check_message'] and status['check_message'].split("\n") or ""
    ret['acknowledged']      = is_status_acknowledged(status)
    ret['overdue']           = is_status_overdue(status, check)

    ret['status_infos'] = []
    keys = status['status_infos'].keys()
    keys.sort()
    for key in keys:
        ret['status_infos'] += [{"sinfo_id" : status['status_infos'][key]['sinfo_id'], "key" : key, "value" : status['status_infos'][key]["value"]}]

    ret['object_infos'] = []
    for key, dic in obj.get('object_infos', {}).iteritems():
        ret['object_infos'] += [{"name" : key, "value" : dic['value'], "link": dic['value'].startswith("http://")}]

    ret['check_infos'] = []
    for key, dic in check.get('check_infos', {}).iteritems():
        ret['check_infos'] += [{"name" : key, "value" : dic['value'], "link" : dic['value'].startswith("http://")}]

    return ret
