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
    input = "Hello World"
    output = trans.translate(input)
    print(output)