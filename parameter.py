#!/usr/bin/env python

class Parameter(object):

from template import Template

    def __init__(self, template, name, value):
        self.__name = name
        self.__value = value
        template.addParam(self)

    def __str__(self):
        return '\"' + self.name + '\" : \"' + str(self.value) + '\"'

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

## end class Parameter()

## begin unit test

if __name__ == '__main__':

    param = Parameter("aName", "aValue")

    print "Parameter:"
    print
    print "  type(param) = " + str(type(param))
    print "  param.name  = " + param.name
    print "  param.value = " + str(param.value)
    print "  str(param)  = " + str(param)
    print
    print "Changing the attributes..."
    print

    param.name = "aNewName"
    param.value = 10

    print "  type(param) = " + str(type(param))
    print "  param.name  = " + param.name
    print "  param.value = " + str(param.value)
    print "  str(param)  = " + str(param)
    print
    
