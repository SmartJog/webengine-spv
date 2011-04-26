from django.db import models

class Check(models.Model):
    chk_id = models.AutoField(primary_key = True)
    plugin = models.CharField(max_length = 4096, null=False, blank=False)
    plugin_check = models.CharField(max_length = 4096, null=False, blank=False)
    name = models.CharField(max_length = 4096, null=False, blank=False)
    repeat = models.PositiveSmallIntegerField(null=False, blank=False, help_text = "In second")
    repeat_on_error = models.PositiveSmallIntegerField(null=False, blank=False, help_text = "In second")

    def __unicode__(self):
        return u"%s:%s:%s" % (self.plugin, self.plugin_check, self.name)

    class Meta:
        db_table = 'checks'

class Group(models.Model):
    grp_id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 4096, null=False, blank=False)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'groups'

class Object(models.Model):
    obj_id = models.AutoField(primary_key = True)
    address = models.CharField(max_length = 4096, null=False, blank=False)
    creation_date = models.DateTimeField(auto_now_add = True, null=False)
    modification_date = models.DateTimeField(auto_now_add = True, auto_now=True)

    def __unicode__(self):
        return u"%s" % (self.address)

    class Meta:
        db_table = 'objects'

class ObjectGroup(models.Model):
    og_id = models.AutoField(primary_key = True)
    object = models.ForeignKey(Object, null=False)
    object.db_column = 'obj_id'
    group = models.ForeignKey(Group, null=False)
    group.db_column = 'grp_id'

    def __unicode__(self):
        return u"%s <-> %s" % (self.group, self.object)

    class Meta:
        db_table = 'objects_group'

class CheckGroup(models.Model):
    cg_id = models.AutoField(primary_key = True)
    check = models.ForeignKey(Check, null=False)
    check.db_column = 'chk_id'
    group = models.ForeignKey(Group, null=False)
    group.db_column = 'grp_id'

    def __unicode__(self):
        return u"%s <-> %s" % (self.group, self.check)

    class Meta:
        db_table = 'checks_group'

class Status(models.Model):
    status_id = models.AutoField(primary_key = True)
    checkgroup = models.ForeignKey(CheckGroup, null=False)
    checkgroup.db_column = 'cg_id'
    objectgroup = models.ForeignKey(ObjectGroup, null=False)
    objectgroup.db_column = 'og_id'
    check_status = models.CharField(max_length = 4096)
    check_message = models.CharField(max_length = 4096)
    last_check = models.DateTimeField(auto_now_add=True)
    next_check = models.DateTimeField(auto_now_add=True)
    sequence = models.IntegerField(null=False, default=0)
    sequence.db_column = 'seq_id'

    def __unicode__(self):
        return u"%s <-> %s <-> %s" % (self.objectgroup.object, self.objectgroup.group, self.checkgroup.check )

    class Meta:
        db_table = 'status'

class StatusInfos(models.Model):
    sinfo_id = models.AutoField(primary_key = True)
    status = models.ForeignKey(Status, null=False)
    status.db_column = 'status_id'
    key = models.CharField(max_length = 4096, null=False)
    value = models.CharField(max_length = 4096)
    creation_date = models.DateTimeField(auto_now_add = True, null=False)
    modification_date = models.DateTimeField(auto_now_add = True, auto_now=True)

    def __unicode__(self):
        return u"%s" % (self.key)

    class Meta:
        db_table = 'status_infos'

class ObjectInfos(models.Model):
    oinfo_id = models.AutoField(primary_key = True)
    object = models.ForeignKey(Object, null=False)
    object.db_column = 'obj_id'
    key = models.CharField(max_length = 4096, null=False)
    value = models.CharField(max_length = 4096)
    creation_date = models.DateTimeField(auto_now_add = True, null=False)
    modification_date = models.DateTimeField(auto_now_add = True, auto_now=True)

    def __unicode__(self):
        return u"%s:%s" % (self.object, self.key)

    class Meta:
        db_table = 'object_infos'

class CheckInfos(models.Model):
    cinfo_id = models.AutoField(primary_key = True)
    check = models.ForeignKey(Check, null=False)
    check.db_column = 'chk_id'
    key = models.CharField(max_length = 4096, null=False)
    value = models.CharField(max_length = 4096)
    creation_date = models.DateTimeField(auto_now_add = True, null=False)
    modification_date = models.DateTimeField(auto_now_add = True, auto_now=True)

    def __unicode__(self):
        return u"%s:%s" % (self.check, self.key)

    class Meta:
        db_table = 'check_infos'
