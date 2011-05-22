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
Bottle: Python Web ���
============================

Bottle�ǿ���,��,������WSGI_��Python_΢��Web���. ���ķ��а�����ǵ�һһ���ļ�ģ��,����`Python��׼�� <http://docs.python.org/library/>`_֮�����κ�����. 


* **·��:** ����--��������֮���ӳ��, ֧�̶ֹ��붯̬URLӳ��.
* **ģ��:** ����,Python��� :ref:`����ģ������ <tutorial-templates>` ,��֧�� mako_, jinja2_ and cheetah_ ģ��.
* **���߼�:** ����ط��ʱ�����,�ļ��ϴ�, Cookies, Headers������HTTP��ص�Ԫ����.
* **������:** ����Http����������,֧��paste_, fapws3_, bjoern_, `Google App Engine <http://code.google.com/intl/en-US/appengine/>`_, cherrypy_ ������WSGI_���ݵ�HTTP������.

.. rubric:: ����: "Hello World" in a bottle

::

  from bottle import route, run

  @route('/:name')
  def index(name='World'):
      return '<b>Hello %s!</b>' % name

  run(host='localhost', port=8080)

.. rubric:: �����밲װ

.. _download:

.. __: https://github.com/defnull/bottle/raw/master/bottle.py

ͨ��PyPi_ (``easy_install -U bottle``)��װ���·��а��������`bottle.py`__ (���ȶ���)�������ĿĿ¼. ����Python��׼��Ϊ,û���κ�ǿ��������ģ��[1]_. Bottle����**Python 2.5+ and 3.x** (ʹ�� 2to3)

�û��ֲ�
===============
�����ϣ��ѧϰ���ʹ��bottle��ܽ���Web����,��������¿�.�������������޷����������, �뽫������ⷢ�ŵ� `�ʼ��� <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   stpl
   api
   plugins/index


����
==============
ָ�Ϻ�HOWTOs.

.. toctree::
   :maxdepth: 2

   tutorial_app
   async
   recipes
   faq


�����빱��
============================

��Щ�½��Ǹ���Щ����Ȥ�˽�bottle�����뷢�����̵Ŀ�����Ա��.

.. toctree::
   :maxdepth: 2

   changelog
   development
   plugindev


.. toctree::
   :hidden:

   plugins/index
   
��Ȩ
==================

������ĵ�������MITЭ��:

.. include:: ../LICENSE.txt
  :literal:

Bottle��Logo��*��*����ЩЭ����!. ����������ͨ��bottle��ҳ��Logo,����δ���޸ĵ�bottle����.
������;����ѯ��!!.

.. rubric:: ��ע

.. [1] ���ʹ��ģ��������������,�ǵ�Ȼ����Ҫ��Ӧ��ģ��������ģ��.

