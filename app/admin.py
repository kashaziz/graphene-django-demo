from tkinter.tix import Form
from django.contrib import admin
from django import forms
from .models import User, Slot, Appointment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'is_active', 'is_staff')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'is_active','last_login', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)


class SlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'created_by')
    list_filter = ('created_by',)
    fieldsets = (
        (None, {
            'fields': ('slot_interval', 'start_time', 'created_by'),
        }),
    )
    search_fields = ('start_time', 'created_by')
    ordering = ('start_time', 'created_by')


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('slot', 'client_name', 'client_email')

    search_fields = ('slot', 'client_name', 'client_email')
    ordering = ('slot', 'client_name', 'client_email')


admin.site.register(User, UserAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Appointment, AppointmentAdmin)

