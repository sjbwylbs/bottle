Bottle Web Framework
====================

.. image:: http://bottlepy.org/bottle-logo.png
  :alt: Bottle Logo
  :align: right

Bottle是一个简单,快速的微型框架,专为小型Web应用而设计的. 它提供包含URL参数的请求
分派(URL路由), 模板, 一个内置Http服务器和许多第三方WSGI/Http服务器适配器与模板引
擎 - 仅一个文件,且无需依赖Python标准库之外的模块.

首页和文档: http://bottle.paws.de/
License: MIT (see LICENSE.txt)

Installation and Dependencies
-----------------------------

执行``pip install bottle``来安装bottle,或者直接`下载 bottle.py <http://pypi.python.org/pypi/bottle>`_ 并放入你的项目文件夹中. 除了Python标准库之外,没有任何强制依赖的第三方模块.


例子
-------

::

    from bottle import route, run

    @route('/hello/:name')
    def hello(name):
        return '<h1>Hello %s!</h1>' % name.title()

    run(host='localhost', port=8080)
