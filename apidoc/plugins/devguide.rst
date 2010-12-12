.. module:: bottle

========================
Plugin Development Guide
========================

Browse the list of :doc:`available plugins </plugins/list>` and see if someone has solved your problem already. If not, then read ahead. This guide explains the `Common Plugin Interface` and how to write your own plugins.


How Plugins Work
================

The plugin API follows the concept of configurable `decorators <http://docs.python.org/glossary.html#term-decorator>`_. To understand plugins, you need to understand the concept and use of decorators first. If you already know what decorators are and how they work, you may want to skip this section.

A decorator is a callable (function, method or class) that takes a callable and returns a new one. Most decorators are used to ``wrap`` a function and alter its arguments and/or return values at runtime. This example does not alter anything, but instead prints some debugging information every time the decorated function is called::

    def decorator(func):
        def wrapper(*args, **kwargs):
            print 'Call arguments:', args, kwargs
            result = func(*args, **kwargs)
            print 'Result:', result
            return result
        return wrapper

Note that a function defined inside another function can refer to variables in the outer function. This is called `nested scope <http://docs.python.org/glossary.html#term-nested-scope>`_ and allows us to access and call `func` from within the nested ``wrapper()`` function.

Lets go one step further: `Decorator factories` or `configurable decorators` are callables that return a decorator::

    def factory(**config):
        def decorator(func):
            def wrapper(*args, **kwargs):
                print 'Call arguments:', args, kwargs
                print 'Configuration:', config
                result = func(*args, **kwargs)
                print 'Result:', result
                return result
            return wrapper
        return decorator

We can reduce the level of nesting and achieve the same by using a class::

    def DecoratorFactory(object):
        def __init__(self, **config):
            self.config = config

        def __call__(self, func):
            ''' This is the actual decorator. '''
            def wrapper(*args, **kwargs):
                print 'Call arguments:', args, kwargs
                print 'Configuration:', self.config
                result = func(*args, **kwargs)
                print 'Result:', result
                return result
            return wrapper



The Common Plugin Interface: :class:`BasePlugin` 
================================================

All plugins are required to subclass :class:`BasePlugin` in order to work with the Bottle plugin interface. The base class defines three abstract methods and subclasses should overwrite at least one of them to be of any use:

.. autoclass:: BasePlugin
   :members:

The :meth:`BasePlugin.setup` method is called immediately after the plugin is installed to an application. You can use it to initialize the plugin.

The :meth:`BasePlugin.close` method is called just before the plugin is removed from an application or the application is closed after a server shutdown. It can be used to clean up temporary files or close database handlers. Please note that this only works for plugins installed to an application. If the plugin is used as a decorator, it must be closed manually.

The :meth:`BasePlugin.wrap` method is called once for each route and can be used to decorate, wrap or replace route callbacks. This method is called on demand only. In other words: A plugin does not know about a route until it is first requested.

Please not that the wrapped callbacks are cached, but the cache is cleared every time the list of installed plugins changes. :meth:`BasePlugin.wrap` may then be called again for the same route. This can happen at any time, even while serving requests.

The following example shows a minimal plugin implementation and is a good starting point for new plugins::

    class DummyPlugin(BasePlugin):
        ''' This plugin does nothing useful. Its name is "Dummy". '''

        def setup(self, app, **config):
            ''' Store configuration for later use. '''
            self.app = app
            self.config = config

        def wrap(self, callback):
            ''' Decorate route callback with a wrapper that does nothing at all. '''
            def wrapper(*a, **ka):
                # Do stuff before the callback is called
                return_value = callback(*a, **ka) # Call the callback
                # Do stuff after the callback is called
                return return_value # Return something
            return wrapper # Return the wrapped callback

        def close(self):
            ''' Do nothing on server shutdown... '''
            pass

Recipe: Middleware Plugins
--------------------------

You do not need the plugin API to install WSGI Middleware to a Bottle application, but is can still be useful::

    class SomeMiddlewarePlugin(BasePlugin):
        def setup(self, app, **config):
            app.wsgi = SomeMiddleware(app.wsgi, **config)

WSGI middleware should not wrap the entire application object, but only the :meth:`Bottle.wsgi` method. This way the app object stays intact and more than one middleware can be applied without conflicts.



Plugin Naming Convention
========================

Bottle is able to locate and install plugins by their name. For this to work, you need to follow a few simple rules:

* The plugin class must inherit from :class:`BasePlugin`.
* The name of the plugin class must end in ``Plugin`` (e.g. ``SQLitePlugin``). 
* Bottle searches for modules or packages named ``bottle_<name>`` where ``<name>`` is the name of the requested plugin (all lower-case). Example: ``bottle_sqlite``



Plugin Example: SqlitePlugin
============================

OK, lets write a plugin that actually does something useful::

    import sqlite3
    import inspect

    def accepts_keyword(func, name):
        ''' Return True if it is save to pass a named keyword argument to
            func. This works even on functions that were previously wrapped
            by another BasePlugin based decorator.
        '''
        while func:
            args, varargs, varkw, defaults = inspect.getargspec(func)
            if name not in args and not varkw:
                return False
            func = getattr(func, '_bottle_wrapped', None)
        return True

    class SQLitePlugin(BasePlugin):
        plugin_name = 'sqlite'

        def setup(self, app, dbfile=':memory:', keyword='db',
                             commit=True, dictrows=True):
            self.dbfile = app.config.get('plugin.sqlite.dbfile', dbfile)
            self.keyword = app.config.get('plugin.sqlite.keyword', keyword)
            self.commit = app.config.get('plugin.sqlite.commit', commit)
            self.dictrows = app.config.get('plugin.sqlite.dictrows', dictrows)

        def wrap(self, callback):
            # Do not wrap callbacks that do not expect a 'db' keyword argument
            if not accepts_keyword(callback, self.keyword):
                return callback
            def wrapper(*args, **kwargs):
                # Connect to the database
                db = self.get_connection()
                # Add the connection handle to the dict of keyword arguments.
                kwargs[self.keyword] = db
                try:
                    rv = callback(*args, **kwargs)
                    if self.commit: db.commit() # Auto-commit
                finally:
                    # Be sure to close the connection.
                    db.close()
                return rv
            return wrapper

        def get_connection(self):
            con = sqlite3.connect(self.dbfile)
            # This allows column access by name: row['column_name']
            if self.dictrows: con.row_factory = sqlite3.Row
            return con

This plugin passes a sqlite3 database handle to callbacks that expect a
`db` parameter. If the callback does not define that parameter, no
connection is made. Not bad for less than 50 lines of code :)

