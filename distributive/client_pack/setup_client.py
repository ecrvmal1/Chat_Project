from setuptools import setup, find_packages

setup(name='msnger_client',
      version="1.0.0",
      description='msnger_client',
      author='Vladimir Malchevskiy',
      author_email='vladimir.malchevskiy@gmail.com',
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
