# -*- coding: utf-8 -*-
import unittest
import bottle
import tools


class MyTestPlugin(bottle.BasePlugin):
    plugin_name = 'mytest'

    def setup(self, app, **config):
        self.app = app
        self.config = config
        c = None

    def wrap(self, func):
        def wrapper(*a, **ka):
            self.lastcall = func, a, ka
            return ''.join(func(*a, **ka)).replace('no-','my-')
        return wrapper

class TestPluginMetaclass(unittest.TestCase):
    def test_missing_name(self):
        def test():
            class BadPlugin(bottle.BasePlugin):
                pass
        self.assertRaises(bottle.PluginError, test)

    def test_double_name(self):
        def test():
            class BadPlugin(bottle.BasePlugin):
                plugin_name = 'mytest'
        self.assertRaises(bottle.PluginError, test)



class TestPluginManagement(tools.ServerTestBase):

    def verify_installed(self, plugin, otype, **config):
        self.assertEqual(type(plugin), otype)
        self.assertEqual(plugin.config, config)
        self.assertEqual(plugin.app, self.app)
        self.assertTrue(plugin in self.app.plugins)
    
    def test_install_by_class(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        self.verify_installed(plugin, MyTestPlugin, foo='bar')

    def test_install_by_instance(self):
        plugin = self.app.install(MyTestPlugin(self.app, foo='bar'))
        self.verify_installed(plugin, MyTestPlugin, foo='bar')

    def test_install_by_name(self):
        plugin = self.app.install('mytest', foo='bar')
        self.verify_installed(plugin, MyTestPlugin, foo='bar')

    def test_install_notfound(self):
        self.assertRaises(ImportError, self.app.install, 'noplugin')

    def test_install_not_a_plugin(self):
        self.assertRaises(bottle.PluginError, self.app.install, type(dict))

    def test_uninstall_by_instance(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        self.app.uninstall(plugin)
        self.assertTrue(plugin not in self.app.plugins)
    
    def test_uninstall_by_type(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        self.app.uninstall(MyTestPlugin)
        self.assertTrue(plugin not in self.app.plugins)

    def test_uninstall_by_name(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        self.app.uninstall('mytest')
        self.assertTrue(plugin not in self.app.plugins)

    def test_plugin_wrapper(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        @self.app.route('/a')
        def a(): return 'no-plugin'
        self.assertBody('my-plugin', '/a')

    def test_plugin_decorator(self):
        plugin = MyTestPlugin(self.app, foo='bar')
        @self.app.route('/a', decorate=[plugin])
        def a(): return 'no-plugin'
        self.assertBody('my-plugin', '/a')

    def test_skip_by_instance(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        @self.app.route('/a', skip=[plugin])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')

    def test_skip_by_type(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        @self.app.route('/a', skip=[MyTestPlugin])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')
        
    def test_skip_by_name(self):
        plugin = self.app.install(MyTestPlugin, foo='bar')
        @self.app.route('/a', skip=['mytest'])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')


if __name__ == '__main__': #pragma: no cover
    unittest.main()
