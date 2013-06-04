from distutils.core import setup


setup(name='whirlwind',
      version='0.1',
      author='Mathieu Lecarme',
      author_email='mlecarme@bearstech.com',
      license='BSD',
      package_dir = {'': 'src'},
      packages= ['whirlwind', 'whirlwind.tornado', 'whirlwind.tornado.carbon', 'whirlwind.tornado.whisper'],
      scripts=['scripts/whirlwind'],
      requires=[
          'tornado(>=3.0)',
          'whisper',
          'pyparsing(==1.5.7)',
          'pytz',
          'flask']
      )
