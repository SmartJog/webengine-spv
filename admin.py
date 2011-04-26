from django.contrib import admin
from spv.models import *

class CheckAdmin(admin.ModelAdmin):
    list_display = ("plugin", "plugin_check", "name", "repeat", "repeat_on_error")
    list_filter = ("plugin", "plugin_check")
    search_fields = list_filter

admin.site.register(Check, CheckAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = list_display

admin.site.register(Group, GroupAdmin)

class ObjectAdmin(admin.ModelAdmin):
    list_display = ("address",)
    search_fields = list_display

admin.site.register(Object, ObjectAdmin)

class ObjectGroupAdmin(admin.ModelAdmin):
    list_display = ("group", "object")
    list_filter = ("group", "object")

admin.site.register(ObjectGroup, ObjectGroupAdmin)

class CheckGroupAdmin(admin.ModelAdmin):
    list_display = ("group", "check")
    list_filter = ("group", "check")

admin.site.register(CheckGroup, CheckGroupAdmin)

class StatusAdmin(admin.ModelAdmin):
    list_display = ("object", "group", "check", "check_status", "check_message")
    list_filter = ("checkgroup", "check_status")
    search_fields = ("check_status", "check_message")

    def object(self, status):
        return status.objectgroup.object

    def group(self, status):
        return status.objectgroup.group

    def check(self, status):
        return status.checkgroup.check

admin.site.register(Status, StatusAdmin)

class StatusInfosAdmin(admin.ModelAdmin):
    list_display = ("object", "group", "check", "key", "value")
    search_fields = ("key", "value")

    def object(self, statusinfos):
        return statusinfos.status.objectgroup.object

    def group(self, statusinfos):
        return statusinfos.status.objectgroup.group

    def check(self, statusinfos):
        return statusinfos.status.checkgroup.check

admin.site.register(StatusInfos, StatusInfosAdmin)

class ObjectInfosAdmin(admin.ModelAdmin):
    list_display = ("object", "key", "value")
    list_filter = ("key", "object")
    search_fields = ("key", "value")

    def object(self, objectinfos):
        return objectinfos.object

admin.site.register(ObjectInfos, ObjectInfosAdmin)

class CheckInfosAdmin(admin.ModelAdmin):
    list_display = ("check", "key", "value")
    list_filter = ("check", "key")
    search_fields = ("key", "value")

    def check(self, checkinfos):
        return checkinfos.check

admin.site.register(CheckInfos, CheckInfosAdmin)
