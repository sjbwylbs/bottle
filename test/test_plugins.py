# -*- coding: utf-8 -*-
import unittest
import bottle
import tools


class TestPluginMetaclass(unittest.TestCase):
    def setUp(self):
        self.old_pdict = bottle.plugin_names.copy()

    def tearDown(self):
        bottle.plugin_names = self.old_pdict

    def test_missing_name(self):
        def test():
            class Plugin(bottle.BasePlugin): pass
        self.assertRaises(bottle.PluginError, test)

    def test_wrong_name(self):
        def test():
            class BadPlug(bottle.BasePlugin): pass
        self.assertRaises(bottle.PluginError, test)

    def test_double_name(self):
        def test():
            class DoublePlugin(bottle.BasePlugin): pass
            class DoublePlugin(bottle.BasePlugin): pass
        self.assertRaises(bottle.PluginError, test)

    def test_overrule_name(self):
        class DoublePlugin(bottle.BasePlugin): pass
        

class TestPluginManagement(tools.ServerTestBase):
    def setUp(self):
        super(TestPluginManagement, self).setUp()
        self.old_pdict = bottle.plugin_names.copy()
        class MyTestPlugin(bottle.BasePlugin):
            def setup(self, app, **config):
                self.app = app
                self.config = config
                c = None
            def wrap(self, func):
                def wrapper(*a, **ka):
                    self.lastcall = func, a, ka
                    return ''.join(func(*a, **ka)).replace('no-','my-')
                return wrapper
        self.pclass = MyTestPlugin

    def tearDown(self):
        super(TestPluginManagement, self).tearDown()
        bottle.plugin_names = self.old_pdict

    def verify_installed(self, plugin, otype, **config):
        self.assertEqual(type(plugin), otype)
        self.assertEqual(plugin.config, config)
        self.assertEqual(plugin.app, self.app)
        self.assertTrue(plugin in self.app.plugins)
    
    def test_install_by_class(self):
        plugin = self.app.install(self.pclass, foo='bar')
        self.verify_installed(plugin, self.pclass, foo='bar')

    def test_install_by_instance(self):
        plugin = self.app.install(self.pclass(self.app, foo='bar'))
        self.verify_installed(plugin, self.pclass, foo='bar')

    def test_install_by_name(self):
        plugin = self.app.install('mytest', foo='bar')
        self.verify_installed(plugin, self.pclass, foo='bar')

    def test_install_notfound(self):
        self.assertRaises(ImportError, self.app.install, 'noplugin')

    def test_install_not_a_plugin(self):
        self.assertRaises(bottle.PluginError, self.app.install, type(dict))

    def test_uninstall_by_instance(self):
        plugin = self.app.install(self.pclass, foo='bar')
        self.app.uninstall(plugin)
        self.assertTrue(plugin not in self.app.plugins)
    
    def test_uninstall_by_type(self):
        plugin = self.app.install(self.pclass, foo='bar')
        self.app.uninstall(self.pclass)
        self.assertTrue(plugin not in self.app.plugins)

    def test_uninstall_by_name(self):
        plugin = self.app.install(self.pclass, foo='bar')
        self.app.uninstall('mytest')
        self.assertTrue(plugin not in self.app.plugins)

    def test_plugin_wrapper(self):
        plugin = self.app.install(self.pclass, foo='bar')
        @self.app.route('/a')
        def a(): return 'no-plugin'
        self.assertBody('my-plugin', '/a')

    def test_plugin_decorator(self):
        plugin = self.pclass(self.app, foo='bar')
        @self.app.route('/a', decorate=[plugin])
        def a(): return 'no-plugin'
        self.assertBody('my-plugin', '/a')

    def test_skip_by_instance(self):
        plugin = self.app.install(self.pclass, foo='bar')
        @self.app.route('/a', skip=[plugin])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')

    def test_skip_by_type(self):
        plugin = self.app.install(self.pclass, foo='bar')
        @self.app.route('/a', skip=[self.pclass])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')
        
    def test_skip_by_name(self):
        plugin = self.app.install(self.pclass, foo='bar')
        @self.app.route('/a', skip=['mytest'])
        def a(): return 'no-plugin'
        self.assertBody('no-plugin', '/a')


if __name__ == '__main__': #pragma: no cover
    unittest.main()
