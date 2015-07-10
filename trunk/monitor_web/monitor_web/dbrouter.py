"""
    monitor_web.dbrouter
    ~~~~~~~~~~~~~

    Redirect the models to its own databases using the meta option named 'verbose_name'.
"""


class DBRouter(object):
    def db_for_read(self, model, **hints):
        return self.__app_router(model)

    def db_for_write(self, model, **hints):
        return self.__app_router(model)

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.verbose_name == obj2._meta.verbose_name:
            return True
        elif obj1._meta.verbose_name in ("default", "cmuserdb") and obj2._meta.verbose_name in ("default", "cmuserdb"):
            return True

    def allow_syncdb(self, db, model):
        return self.__app_router(model) == db

    def __app_router(self, model):
        if model._meta.verbose_name == "cmuser":
            return 'cmuserdb'
        elif model._meta.verbose_name == "novadb":
            return 'novadb'
        else :
            return 'default'