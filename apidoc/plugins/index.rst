.. module:: bottle

==============
Plugins
==============

Bottles core features cover most of the common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. They add missing functionality to the framework, integrate third party libraries or just automate some repetitive work.

We have a growing :doc:`/plugins/list` and most plugins are designed to be portable and re-usable across applications. The chances are high that your problem has already been solved and a ready-to-use plugin exists. If not, the :doc:`/plugins/devguide` may help you.

The effects and APIs of plugins are manifold and depend on the specific plugin. The 'sqlite' plugin for example detects callbacks that require a ``db`` keyword argument and creates a fresh database connection object every time the callback is called. This makes it very convenient to use a database::

    from bottle import route, install, template
    install('sqlite', dbfile='/tmp/test.db')

    @route('/show/:post_id')
    def show(db, post_id):
        c = db.execute('SELECT title, content FROM posts WHERE id = ?', (int(post_id),))
        row = c.fetchone()
        return template('show_post', title=row['title'], text=row['content'])

    @route('/contact')
    def contact_page():
        ''' This callback does not need a db connection. Because the 'db'
            keyword argument is missing, the sqlite plugin ignores this callback
            completely. '''
        return template('contact')

Other plugin may populate the thread-save :data:`local` object, change details of the :data:`request` object, filter the data returned by the callback or bypass the callback completely. An "auth" plugin for example could check for a valid session and return a login page instead of calling the original callback. What happens exactly depends on the plugin.


Using Plugins
==================

Plugins can be installed application-wide or just to some specific routes that need additional functionality. Most plugins are save to be installed to all routes and are smart enough to not add overhead to callbacks that do not need their functionality.

Let us take the 'sqlite' plugin for example. It only affects route callbacks that need a database connection. Other routes are left alone. Because of this, we can install the plugin application-wide with no additional overhead.


Application-wide Installation
-----------------------------

To install a plugin, just call :func:`install` with a plugin name or class as first argument. Any additional arguments are passed on to the plugin as configuration::

    # install by name
    install('SQLite', dbfile='/tmp/test.db')
    
    # install by class
    from bottle_sqlite import SQLitePlugin
    install(SQLitePlugin, dbfile='/tmp/test.db')

The first way (install by name) is a shortcut and works for all plugins that follow the :doc:`/plugins/devguide`. Bottle locates and imports the plugin module or package automatically.

.. note::
    The module-level :func:`install` function installs plugins to the default application. To install a plugin to a specific application, use the :meth:`Bottle.install` method on the application object instead.

The plugin is initialized and configured immediately, but not applied to the route callbacks yet. This is delayed to make sure no routes are missed. You can install plugins first and add routes later, if you want to. The order of installed plugins is significant, though. If a plugin requires a database connection, you need to install the database plugin first.

.. rubric:: Uninstall Plugins

You can use a name, class or instance to :func:`uninstall` a previously installed plugin::

    uninstall('sqlite')     # uninstall by name
    uninstall(SQLitePlugin) # uninstall by class

Plugins can be installed and removed at any time, even at runtime while serving requests. This enables some neat tricks (installing slow debugging or profiling plugins only when needed) but should not be overused. Each time the list of plugins changes, the route cache is flushed and all plugins are re-applied.


Route-specific Installation
---------------------------

Instances of plugins double as decorators. This comes in handy if you want to install a plugin to only a small number of routes::

    sqlite_decorator = SQLitePlugin(dbfile='/tmp/test.db')

    @route('/create')
    @sqlite_decorator
    def create(db):
        db.execute('INSERT INTO ...')

Even if this plugin only affects a single route, it is connected to the default application and able to access its configuration dictionary (:attr:`Bottle.config`). To connect the plugin to a different application object, pass it as a positional argument during initialisation::

    app = bottle.Bottle()
    sqlite_decorator = SQLitePlugin(app, dbfile='/tmp/test.db')

    @app.route('/create')
    @sqlite_decorator
    def create(db):
        db.execute('INSERT INTO ...')


Blacklist Plugins
-----------------

You may want to explicitly disable a plugin for a number of routes. The :func:`route` decorator has a ``skip`` parameter for this purpose::

    # Install the SQLite plugin to all routes and save the handle for later use.
    sqlite_plugin = install('SQLite')

    # Skip the SQLite plugin for this route.
    @route('/open/:db', skip=['SQLite'])
    def open_db(db):
        # The 'db' keyword argument is not touched by the plugin this time.
        if db in ('test', 'test2'):
            # The plugin handle can be used for runtime configuration, too.
            sqlite_plugin.dbfile = '/tmp/%s.db' % db
            return "Database File switched to: /tmp/%s.db" % db
        abort(404, "No such database.")

The ``skip`` parameter accepts a single value or a list of values. You can use a name, class or instance to identify the plugin that is to be skipped. Set ``skip=True`` to skip all plugins at once.


