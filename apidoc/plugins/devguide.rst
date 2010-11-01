========================
Plugin Development Guide
========================

Browse the list of :doc:`available plugins </plugins/index>` and see if someone has solved your problem already. If not, then read ahead. This guide explains the `Common Plugin Interface`.

Writing Plugins
==================

The plugin API follows the concept of configurable decorators that are applied to all or a subset of all routes of an application. Decorators are a very flexible and pythonic way to reduce repetitive work. A common base class (:class:`BasePlugin`) is used to simplify plugin development and ensure portability.

.. rubric:: Short Introduction to Decorators

Basically a decorator is a function that takes a callable object and returns a new one. Most decorators are used to create `wrapper` functions that wrap the original and alter its input and/or return values at runtime. Accordingly, `decorator factories` or `configurable decorators` are functions or classes that return a decorator::

    def factory(**config):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Alter args or kwargs
                rv = func(*args, **kwargs) # Call original function
                # Alter return value
                return rv
            return wrapper
        return decorator

Inner functions have access to the local variables of the outer function they were defined in. This is why the ``wrapper()`` function in this example is able to call ``func`` internally or access the config-dict passed to the factory.


Common Plugin Interface: :class:`BasePlugin` 
--------------------------------------------

All plugins inherit from :class:`BasePlugin` and override the :meth:`BasePlugin.setup` and :meth:`BasePlugin.wrap` methods as needed. This example shows a minimal plugin implementation and is a good starting point for new plugins::

    class DummyPlugin(BasePlugin):
        ''' This plugin does nothing useful. '''

        def setup(self, app, **config):
            ''' This is called only once during plugin initialisation.
            
                :param app: is an application object (Bottle instance).
                :param **config: contains additional configuration.
            '''
            self.app = app
            self.config = config

        def wrap(self, callback):
            ''' This decorator is applied to each route callback. '''
            # @functools.wraps(func) is not needed. Bottle does that for you.
            def wrapper(*a, **ka):
                # Do stuff before the callback is called
                return_value = callback(*a, **ka) # Call the callback
                # Do stuff after the callback is called
                return return_value # Return something
            return wrapper # Return the wrapped callback

This plugin does nothing useful but TODO

* The ``setup(app, **config)`` method is called once during plugin initialisation. The first parameter is an instance of :class:`Bottle` and equals the default application if the user did not specify a different one. Additional parameters may be accepted or required for configuration.
* The :meth:`BasePlugin.wrap` method is called once for each installed route callback and receives the callback as its only argument. It should return a callable and double as a decorator.
* You may add additional methods and attributes as needed. Just make sure that the ``__init__`` and ``__call__`` methods of the base class remain available.

Plugin Naming Convention
------------------------

Bottle is able to locate and install plugins by their name. For this to work, you need to follow a simple naming convention:

* The plugin class must inherit from :class:`BasePlugin`.
* The name of the plugin class must end in ``Plugin`` (e.g. ``SomethingPlugin``). 
* Bottle searches for modules or packages named ``bottle_<name>`` where ``<name>`` is the name of the requested plugin (all lower-case).



.. rubric:: Middleware Plugins

You do not need the plugin API to install WSGI Middleware to a Bottle application, but is can still be useful::

    class SomeMiddlewarePlugin(BasePlugin):
        plugin_name = 'some_middleware'

        def setup(self, app, **config):
            app.wsgi = SomeMiddleware(app.wsgi, **config)

WSGI middleware should not wrap the entire application object, but only the :meth:`Bottle.wsgi` method. This way the app object stays intact and more than one middleware can be applied without conflicts.



Behind the Scenes: Runtime Plugin Management
--------------------------------------------

Plugins are applied on demand only. In other words: A plugin does not know about a route callback until the route is first requested.

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

