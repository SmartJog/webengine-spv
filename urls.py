from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _


urlpatterns = patterns('spv',
    url(r'^$', 'views.index', name='spv-index'),
    url(r'^sort/(?P<sort>\w+)/(?P<column>\d+)$', 'views.index', name='spv-sort'),
    url(r'^status/details/(?P<status_id>\d+)/$', 'views.status_details', name='spv-status-details'),
    url(r'^status/reschedule/(?P<status_id>\d+)/$', 'views.status_reschedule', name='spv-status-reschedule'),
    url(r'^status/acknowledge/(?P<status_id>\d+)/$', 'views.status_acknowledge', name='spv-status-acknowledge'),
)
