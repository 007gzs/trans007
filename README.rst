#############
Translate API
#############

install
=======
.. code-block:: bash

    pip install trans007


use
=======
.. code-block:: python

    from trans007 import GoogleTranslate
    trans = GoogleTranslate()
    # trans = GoogleTranslate(proxies={'https': '127.0.0.1:7890'})
    print(trans.translate("Hello World", 'en', 'zh-CN'))