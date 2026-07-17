from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class AudioLuxAdminSite(AdminSite):
    """Custom Admin Site for Audio Lux"""
    site_header = "Audio Lux Administration"
    site_title = "Audio Lux Admin"
    index_title = "Dashboard"
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['index_title'] = self.index_title
        return context