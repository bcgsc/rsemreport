from django.conf.urls import patterns, include, url

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'rsemreport.views.home', name='home'),
    url(r'^passed_GSEs$', 'rsemreport.views.passed_GSEs', name='passed_GSEs'),
    url(r'^not_passed_GSEs$', 'rsemreport.views.not_passed_GSEs', name='not_passed_GSEs'),
    url(r'^stats$', 'rsemreport.views.stats', name='stats'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)


# NOT for production use!
# https://docs.djangoproject.com/en/1.6/howto/static-files/
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

