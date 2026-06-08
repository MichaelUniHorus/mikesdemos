# routers.py - Database routing for multi-app architecture
# Каждое приложение использует свою БД для изоляции и масштабирования

class AuthRouter:
    """
    Роутер для управления операциями с моделями аутентификации.
    Использует default БД для auth, sessions, contenttypes
    """
    auth_models = {'auth', 'sessions', 'contenttypes', 'admin'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.auth_models:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.auth_models:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.auth_models or obj2._meta.app_label in self.auth_models:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.auth_models:
            return True
        return None


class OrganizationsRouter:
    """Роутер для приложения organizations (opencbbl)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'organizations':
            return 'opencbbl_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'organizations':
            return 'opencbbl_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'organizations' or obj2._meta.app_label == 'organizations':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'organizations':
            return db == 'opencbbl_db'
        return None


class ApiRouter:
    """Роутер для приложения api (opencbbl)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'api':
            return 'opencbbl_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'api':
            return 'opencbbl_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'api' or obj2._meta.app_label == 'api':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'api':
            return db == 'opencbbl_db'
        return None


class AccountsRouter:
    """Роутер для приложения accounts (pcmanager)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'accounts':
            return 'pcmanager_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'accounts':
            return 'pcmanager_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'accounts' or obj2._meta.app_label == 'accounts':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'accounts':
            return db == 'pcmanager_db'
        return None


class InventoryRouter:
    """Роутер для приложения inventory (pcmanager)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'inventory':
            return 'pcmanager_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'inventory':
            return 'pcmanager_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'inventory' or obj2._meta.app_label == 'inventory':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'inventory':
            return db == 'pcmanager_db'
        return None


class BuildsRouter:
    """Роутер для приложения builds (pcmanager)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'builds':
            return 'pcmanager_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'builds':
            return 'pcmanager_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'builds' or obj2._meta.app_label == 'builds':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'builds':
            return db == 'pcmanager_db'
        return None


class DashboardRouter:
    """Роутер для приложения dashboard (pcmanager)"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'dashboard':
            return 'pcmanager_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'dashboard':
            return 'pcmanager_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'dashboard' or obj2._meta.app_label == 'dashboard':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'dashboard':
            return db == 'pcmanager_db'
        return None
