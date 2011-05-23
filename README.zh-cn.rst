Bottle Web Framework
====================

.. image:: http://bottlepy.org/bottle-logo.png
  :alt: Bottle Logo
  :align: right

Bottle��һ����,���ٵ�΢�Ϳ��,רΪС��WebӦ�ö���Ƶ�. ���ṩ����URL����������
����(URL·��), ģ��, һ������Http����������������WSGI/Http��������������ģ����
�� - ��һ���ļ�,����������Python��׼��֮���ģ��.

��ҳ���ĵ�: http://bottle.paws.de/
License: MIT (see LICENSE.txt)

Installation and Dependencies
-----------------------------

ִ��``pip install bottle``����װbottle,����ֱ��`���� bottle.py <http://pypi.python.org/pypi/bottle>`_ �����������Ŀ�ļ�����. ����Python��׼��֮��,û���κ�ǿ�������ĵ�����ģ��.


����
-------

::

    from bottle import route, run

    @route('/hello/:name')
    def hello(name):
        return '<h1>Hello %s!</h1>' % name.title()

    run(host='localhost', port=8080)
