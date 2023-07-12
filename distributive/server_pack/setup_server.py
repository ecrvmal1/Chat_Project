from setuptools import setup, find_packages

setup(name='msnger_server',
      version="1.0.0",
      description='msnger_server',
      author='Vladimir Malchevskiy',
      author_email='vladimir.malchevskiy@gmail.com',
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
