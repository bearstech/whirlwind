from distutils.core import setup


setup(name='whirlwind',
      version='0.2',
      author='Mathieu Lecarme',
      author_email='mlecarme@bearstech.com',
      license='BSD',
      package_dir = {'': 'src'},
      packages= ['whirlwind'],
      requires=[
          'whisper',
          'pyparsing(==1.5.7)',
          'pytz',
          'bottle']
      )
