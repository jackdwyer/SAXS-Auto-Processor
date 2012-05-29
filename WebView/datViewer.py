import cherrypy
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
from simplejson import JSONEncoder
import simplejson
from Core import DatFile


encoder = JSONEncoder()
datFile = DatFile.DatFile("35C_naPhos_nacl_ph7c_0128.dat")

class datPage(object):
    def index(self):
        return (simplejson.dumps(datFile.getValues()))
    index.exposed = True


class HelloWorld(object):
    dat = datPage()
    def index(self):
        tmpl = env.get_template('datGraph.html')
        return tmpl.render(salutation='Hello', target='World')
        #return "Hello World!"
    index.exposed = True
    



cherrypy.quickstart(HelloWorld())