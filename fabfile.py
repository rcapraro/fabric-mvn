# -*- coding: iso-8859-15 -*-
from fabric.api import *
#from fabric.utils import puts
from fabric.colors import red,green
from fabric.contrib.files import exists
# from fabric.network import ssh

env.roledefs = {
	'deploy':['vmubuntu'],
	'build':['localhost']
}
env.user = 'richard'
env.password = 'tapiola74'
#env.key_filename = '~/vmubuntu.key'
#env.parallel=True


# modules path relative to the parent pom
modules_path = "./"

# list of modules to deploy
modules = [
    "webapp1",
    "webapp2"
]

tomcat_home = '/var/lib/tomcat7'

@task
def deploy():
    """
    Build & déploiement des wars sur tomcat7
    """
    execute(build)
    execute(tomcat_shutdown)

    for module in modules:
        execute(remove_cache, module)
        execute(upload_war, module)

    execute(tomcat_startup)


@roles('build')
def build(maven_test_skip=False, maven_offline=False):
    """
    Build maven
    """  
    local('mvn clean install -Dmaven.test.skip=%(skip)s %(extra)s' % {
    'skip': maven_test_skip,
    'extra': '-o' if maven_offline else ''
    })
    print(green('Build maven de l\'application terminé',True))


@roles('deploy')
def tomcat_shutdown():
    """
    Arrêt de tomcat7
    """
    run('sudo service tomcat7 stop')
    print(green('Arrêt de tomcat7 terminé',True))


@roles('deploy')
def remove_cache(module):
    """
    Suppression du cache
    """

    module_cache = '%(tomcat_home)s/work/Catalina/localhost/%(module)s' % {
        'tomcat_home' : tomcat_home,
        'module' : module
    }

    if exists(module_cache):
        run('sudo rm -rf %s' % module_cache)

    print(green('Suppression du cache de %s des wars terminé' % module, True))

@roles('deploy')
def upload_war(module):
    """
    Deploiement des wars.
    """
    module_war = modules_path + ('%s' % module) + '/target/' + ('%s.war' % module);
    put('%s' % module_war, '%s/webapps/' % tomcat_home, use_sudo=True)
    print(green('Déploiement du war %s terminé' % module, True))


@roles('deploy')
def tomcat_startup():
    """
    Démarrage de tomcat7
     """
    run('sudo service tomcat7 start')
    print(green('Redémarrage de tomcat7 terminé', True))