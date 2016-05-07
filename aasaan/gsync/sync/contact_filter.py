__author__ = 'dpack'

from .filter_base import ContactSync
from .settings import contact_header


class ContactFilterInactive(ContactSync):
    def filter_row(contact_role, contact_role_model):
        if not contact_role:
            return tuple()

        if contact_role_model.contact.get_status_display() in ['Inactive', 'Deceased']:
            return tuple()

        return contact_header(*contact_role)


class ContactFilterAdminRole(ContactSync):
    def filter_row(contact_role, contact_role_model):
        if not contact_role:
            return tuple()

        if contact_role_model.role.admin_role:
            return tuple()

        return contact_header(*contact_role)
