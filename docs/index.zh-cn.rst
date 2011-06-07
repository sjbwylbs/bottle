.. highlight:: python
.. currentmodule:: bottle

.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: http://jinja.pocoo.org/2/
.. _paste: http://pythonpaste.org/
.. _fapws3: https://github.com/william-os4y/fapws3
.. _bjoern: https://github.com/jonashaag/bjoern
.. _flup: http://trac.saddi.com/flup
.. _cherrypy: http://www.cherrypy.org/
.. _WSGI: http://www.wsgi.org/wsgi/
.. _Python: http://python.org/
.. _testing: https://github.com/defnull/bottle/raw/master/bottle.py
.. _issue_tracker: https://github.com/defnull/bottle/issues
.. _PyPi: http://pypi.python.org/pypi/bottle

============================
Bottle: Python Web 框架
============================

Bottle是快速,简单,轻量级WSGI_的Python_微型Web框架. 它的发行版仅仅是单一一个文件模块,除了`Python标准库 <http://docs.python.org/library/>`_之外无任何依赖. 


* **路由:** 请求--方法调用之间的映射, 支持固定与动态URL映射.
* **模板:** 快速,Python风格 :ref:`内置模板引擎 <tutorial-templates>` ,且支持 mako_, jinja2_ and cheetah_ 模板.
* **工具集:** 方便地访问表单数据,文件上传, Cookies, Headers和其他HTTP相关的元数据.
* **服务器:** 内置Http开发服务器,支持paste_, fapws3_, bjoern_, `Google App Engine <http://code.google.com/intl/en-US/appengine/>`_, cherrypy_ 或其他WSGI_兼容的HTTP服务器.

.. rubric:: 例子: "Hello World" in a bottle

::

  from bottle import route, run

  @route('/:name')
  def index(name='World'):
      return '<b>Hello %s!</b>' % name

  run(host='localhost', port=8080)

.. rubric:: 下载与安装

.. _download:

.. __: https://github.com/defnull/bottle/raw/master/bottle.py

通过PyPi_ (``easy_install -U bottle``)安装最新发行版或者下载`bottle.py`__ (非稳定版)到你的项目目录. 除了Python标准库为,没有任何强制依赖的模块[1]_. Bottle兼容**Python 2.5+ and 3.x** (使用 2to3)

用户手册
===============
如果你希望学习如何使用bottle框架进行Web开发,请继续往下看.如果这里的内容无法解答你问题, 请将你的问题发信到 `邮件组 <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   stpl
   api
   plugins/index


基础
==============
指南和HOWTOs.

.. toctree::
   :maxdepth: 2

   tutorial_app
   async
   recipes
   faq


开发与贡献
============================

这些章节是给那些有兴趣了解bottle开发与发布流程的开发人员的.

.. toctree::
   :maxdepth: 2

   changelog
   development
   plugindev


.. toctree::
   :hidden:

   plugins/index
   
授权
==================

代码和文档都基于MIT协议:

.. include:: ../LICENSE.txt
  :literal:

Bottle的Logo并*不*在这些协议下!. 它允许被用于通往bottle主页的Logo,或者未曾修改的bottle里面.
其他用途请先询问!!.

.. rubric:: 附注

.. [1] 如果使用模板或服务器适配器,那当然还需要相应的模板或服务器模块.

