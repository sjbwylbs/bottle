.. module:: bottle

=========================
List of available Plugins
=========================

The plugin API is extremely flexible and most plugins are designed to be portable and re-usable across applications. Below is an incomplete list of available plugins, all tested with the latest version of bottle and ready to use.

Have a look at :doc:`/plugins/index` for general questions about plugins (installation, usage). If you plan to develop a new plugin, the :doc:`/plugins/devguide` may help you.


SQLite Plugin
----------------------

* **Autor:** Marcel Hellkamp
* **Licence:** MIT
* **Installation:** Included
* **Documentation:** :doc:`/plugins/sqlite`
* **Description:** Provides an sqlite database connection handle to callbacks that request it.


Werkzeug Plugin
----------------------

* **Autor:** Marcel Hellkamp
* **Licence:** MIT
* **Installation:** ``pip install Bottle-Werkzeug``
* **Documentation:** :doc:`/plugins/werkzeug`
* **Description:** Integrates the "werkzeug" library (alternative request and response objects, advanced debugging middleware and more).


Profile Plugin
----------------------

* **Autor:** Marcel Hellkamp
* **Licence:** MIT
* **Installation:** ``pip install Bottle-Profile``
* **Documentation:** :doc:`/plugins/profile`
* **Description:** This plugin collects profiling data and displays it in the browser.

