.. module:: bottle

========================
Plugin Development Guide
========================

Browse the list of :doc:`available plugins </plugins/index>` and see if someone has solved your problem already. If not, then read ahead. This guide explains the `Common Plugin Interface` and how to write your own plugins.


How Plugins Work
================

The plugin API follows the concept of configurable decorators. To understand plugins, you need to understand the concept and use of decorators first. If you already know what decorators are and how they work, you may want to skip this section.

A decorator is a callable (function, method or class) that takes a callable and returns a new one. Most decorators are used to create `wrapper` functions that wrap the original and alter its input and/or return values at runtime::

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Alter args or kwargs
            rv = func(*args, **kwargs) # Call original function
            # Alter return value
            return rv
        return wrapper

In Python, functions are objects and you can define new functions at runtime. Additionally, if a variable is not found in the local namespace of a function, it is searched in the namespace the function was defined in. This is called `nested scope` and allows the ``wrapper()`` function in the last example to access and call ``func``, even if ``func`` originally belongs to the namespace of the ``decorator()`` function.

Lets go one step further: `Decorator factories` or `configurable decorators` are functions that return a decorator::

    def factory(**config):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Alter args or kwargs
                rv = func(*args, **kwargs) # Call original function
                # Alter return value
                return rv
            return wrapper
        return decorator

Again, each function has access to all namespaces up to the global namespace thanks to `nested scoping`. A class-based decorator factory works very similar::

    def DecoratorFactory(object):
        def __init__(self, **config):
            self.config = config
        def __call__(self, func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper



The Common Plugin Interface: :class:`BasePlugin` 
================================================

All plugins are required to subclass :class:`BasePlugin` in order to work with the Bottle plugin interface. The base class defines three abstract methods and subclasses should overwrite at least one of them to be of any use:

.. autoclass:: BasePlugin
   :members:

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




Behind the Scenes
========================

The Plugin API does more than just decoration route callbacks. It keeps track of installed plugins and ensures that new route are decorated properly and new plugins are applied to all routes including old ones.

TODO: Explain on-demand decorating and callback caching.

Plugins are applied on demand only. In other words: A plugin does not know about a route callback until the route is first requested.


The return value of :meth:`BasePlugin.wrap` is cached and the cache is cleared every time the list of installed plugins changes.



The return value of :meth:`BasePlugin.wrap` is cached and the cache is cleared every time the list of installed plugins changes. This can happen at any time, even at runtime. What does this mean for a plugin development?

  * The :meth:`BasePlugin.wrap` method is called once for each route callback most of the time, but may be called again after the cache is flushed or never. 


Plugins may be installed or removed at any time, even at runtime while serving requests.

The :meth:`BasePlugin.setup` method is called once during plugin initialisation.

The :meth:`BasePlugin.wrap` method is called on demand and the result is cached. In other words: 


 A plugin can call :meth:`Bottle.reset_plugins` to clear the cache and force all plugins to be reapplied.


calls the setup-routine of the plugin and connects it to the application. The plugin is not applied to the route callbacks yet. This is delayed to make sure no routes get missed. You can install plugins first and add routes later.



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

