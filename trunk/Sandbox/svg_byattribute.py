#########################################################################
# Not clear that we want this
#########################################################################
#
#   def __getattr__(self, name):
#     return self.attrib[self._preprocess_attribname(name)]
#
#   def __setattr__(self, name, value):
#     if name in self.__dict__:
#       self.__dict__[name] = value
#     else:
#       self.attrib[self._preprocess_attribname(name)] = value
#
#   def __delattr__(self, name):
#     if name not in self.__dict__:
#       del self.attrib[self._preprocess_attribname(name)]
#
#   def __str__(self): return repr(self)
#
#   def __iter__(self): return iter(self.children)
#########################################################################
