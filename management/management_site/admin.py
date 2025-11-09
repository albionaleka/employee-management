from django.contrib import admin
from .models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'email', 'city', 'state', 'tenant_id', 'tenant_user', 'created_at')
	search_fields = ('first_name', 'last_name', 'email', 'tenant_id', 'city', 'state')
	list_filter = ('state', 'created_at')
	readonly_fields = ('created_at', 'tenant_id')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(tenant_id=request.user.username)

	def tenant_user(self, obj):
		if not obj.tenant_id:
			return "(none)"
		try:
			return User.objects.get(pk=int(obj.tenant_id))
		except Exception:
			return obj.tenant_id

	tenant_user.short_description = 'Tenant (User)'

	def save_model(self, request, obj, form, change):
		if not change or not obj.tenant_id:
			obj.tenant_id = request.user.username
		super().save_model(request, obj, form, change)

	def has_change_permission(self, request, obj=None):
		has_perm = super().has_change_permission(request, obj)
		if not has_perm:
			return False
		if obj is None:
			return True
		if request.user.is_superuser:
			return True
		return obj.tenant_id == request.user.username

	def has_delete_permission(self, request, obj=None):
		has_perm = super().has_delete_permission(request, obj)
		if not has_perm:
			return False
		if obj is None:
			return True
		if request.user.is_superuser:
			return True
		return obj.tenant_id == request.user.username


admin.site.register(Employee, EmployeeAdmin)
