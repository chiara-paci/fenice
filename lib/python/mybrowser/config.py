from collections.abc import Mapping

class ConfigDict(Mapping):
    _base={}
    _actions=[]

    def __init__(self):
        self._objects=[]
        self._parents={}
        self._app={}
        self._actions_by_object={}

    def add_object(self,app_label,label,parent="",extra_actions=[]):
        self._objects.append(label)
        self._app[label]=app_label
        if parent:
            self._parents[label]=parent
        if extra_actions:
            self._actions_by_object[label]=extra_actions

    def __getitem__(self, key):
        t=key.split("_")
        if (len(t)>=2) and (t[0] in self._objects):
            label=t[0]
            app_label=self._app[label]
            action="_".join(t[1:])
            if action in [ "update","detail" ]:
                return "/%s/%s/%%(id)d/" % (app_label,label)
            if action in [ "delete" ]:
                return "/%s/%s/%%(id)d/delete/" % (app_label,label)
            if action in [ "list", "create"]:
                return "/%s/%s/" % (app_label,label)
        return self._base[key]

    def __contains__(self, key):
        t=key.split("_")
        if (len(t)>=2) and (t[0] in self._objects):
            label=t[0]
            action="_".join(t[1:])
            if action in self._actions:
                return True
            if label in self._actions_by_object:
                if action in self._actions_by_object[label]:
                    return True
        return key in self._base

    def __len__(self):
        L=len(self._base)
        L+=len(self._actions)*len(self._objects)
        for k in self._actions_by_object:
            L+=len(self._actions_by_object[k])
        return L

    def __iter__(self):
        class Iterator(object):
            def __init__(self,base,objects,actions,actions_by_object):
                self._base=base
                self._objects=objects
                self._actions=actions
                self._actions_by_object=actions_by_object
                self._ind=0

                self._list=[]
                for obj in self._base:
                    self._list.append(obj)
                for obj in self._objects:
                    for action in self._actions:
                        self._list.append(self._objects[obj]+"_"+action)
                    if obj not in self._actions_by_object: continue
                    for action in self._actions_by_object[obj]:
                        self._list.append(self._objects[obj]+"_"+action)
                self._L=len(self._list)

            def __iter__(self):
                return self

            def __next__(self):
                if self._ind > self._L:
                    raise StopIteration
                obj=self._list[self._ind]
                self._ind+=1
                return obj
        return Iterator(self._base.keys(),self._objects,self._actions,self._actions_by_object)

