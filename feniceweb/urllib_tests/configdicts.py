from mybrowser.config import ConfigDict

COMMUNITY_NAME="Costruttori di Mondi"

class UrlsDict(ConfigDict):
    _base={
        "home": "/",
        #"who-we-are": "/who-we-are/",
        #"contacts": "/contacts/",
        "credits": "/credits/",
        "policy": "/privacy/policy/",

        # feniceauth (accounts) - da finire
        "login": "/accounts/login/",
        "logout": "/accounts/logout/",
        "register": "/accounts/register/",
        "profile": "/accounts/profile/",
        #"working": "/accounts/working/",
    }
    #_actions=[ "list", "create", "update", "detail", "delete"]

class TitlesDict(ConfigDict):
    _base={
        "home": "Welcome to %s!" % COMMUNITY_NAME,
        #"who-we-are": "Who we are",
        #"contacts": "Contacts",
        "credits": "Credits",
        "policy": "Privacy Policy",

        # feniceauth (accounts) - da finire
        "login": "Login",
        "logout": "Logged Out",
        "profile": "%(user)s",
    }
    #_actions=["list","detail","delete"]

    def __getitem__(self, key):
        t=key.split("_")
        if (len(t)>=2) and (t[0] in self._objects):
            label=t[0]
            action="_".join(t[1:])
            if action == "list":
                return "%(label)ss" % {"label": label.capitalize() }
            if action == "detail":
                return "%%(%(label)s)s" % {"label": label}
            if action == "delete":
                return "Deleting %%(%(label)s)s" % {"label": label}
            if label in self._actions_by_object:
                if action in self._actions_by_object[label]:
                    i_type=action.split("_")
                    i_type=" ".join([x.capitalize() for x in i_type])
                    return "%(i_type)s" % {"i_type": i_type}
        return self._base[key]

class WinTitlesDict(ConfigDict):
    _prefix="%s - " COMMUNITY_NAME

    _base={

        "home": _prefix+"Welcome to %s!" % COMMUNITY_NAME,
        #"who-we-are": _prefix+"Who we are",
        #"contacts": _prefix+"Contacts",
        "credits": _prefix+"Credits",
        "policy": _prefix+"Privacy Policy",

        # feniceauth (accounts)
        "profile": _prefix+"%(user)s's Profile",
        "login": _prefix+"Login",
        "logout": _prefix+"Logged Out",
        "home": _prefix+"Welcome!",
    }

    #_actions=["list","detail","delete"]

    def __getitem__(self, key):
        t=key.split("_")
        if (len(t)>=2) and (t[0] in self._objects):
            label=t[0]
            action="_".join(t[1:])
            if action == "list":
                if not label in self._parents:
                    return self._prefix + "%(label)ss" % {"label": label.capitalize() }
                fmt=self._prefix + "%%(%(parent)s)s - %(label)ss"
                return fmt % { "parent": self._parents[label],"label": label.capitalize() }
            if action == "detail":
                return self._prefix + "%%(%(label)s)s" % {"label": label}
            if action == "delete":
                return self._prefix + "deleting %%(%(label)s)s" % {"label": label}
            if label in self._actions_by_object:
                if action in self._actions_by_object[label]:
                    i_type=action.split("_")
                    i_type=" ".join([x.capitalize() for x in i_type])
                    return self._prefix + "%%(%(label)s)s - %(i_type)s" % { "label": label, 
                                                                            "i_type": i_type }
        return self._base[key]

class FormsDict(ConfigDict):
    _base={
        "login": "login",
    }
    _actions=["create","update","delete"]

    def __getitem__(self, key):
        t=key.split("_")
        if (len(t)>=2) and (t[0] in self._objects):
            label=t[0]
            action="_".join(t[1:])
            if action == "create":
                return "%(label)s_create" % {"label": label}
            if action == "update":
                return "%(label)s_update_%%(id)d" % {"label": label}
            if action == "delete":
                return "%(label)s_delete_%%(id)d" % {"label": label}
            if label in self._actions_by_object:
                if action in self._actions_by_object[label]:
                    return "%(label)s_%(action)s_%%(id)d" % {"label": label,"action": action}
        return self._base[key]

# class ButtonsDict(ConfigDict):
#     _base={}
#     _actions=["create","update","delete"]

#     def __getitem__(self, key):
#         t=key.split("_")
#         if (len(t)>=2) and (t[0] in self._objects):
#             label=t[0]
#             action="_".join(t[1:])
#             if action == "create":
#                 return "create a new %(label)s" % {"label": label}
#             if action == "update":
#                 return "update %(label)s" % {"label": label}
#             if action == "delete":
#                 return "delete %(label)s" % {"label": label}
#             if label in self._actions_by_object:
#                 if action in self._actions_by_object[label]:
#                     return "%(action)s %(label)s" % {"label": label,"action": action}
#         return self._base[key]

NAVBARS = {
    "mainbar": "mainbar",
}

URLS=UrlsDict()
TITLES=TitlesDict()
WIN_TITLES=WinTitlesDict()

FORMS=FormsDict()
#BUTTONS=ButtonsDict()
#SECTIONS = {}



for app_label,label,kwargs in [ 
        ("fenicestat","browser", {"extra_actions": [ "list","create"]}),
]:
    TITLES.add_object(app_label,label,**kwargs)
    URLS.add_object(app_label,label,**kwargs)
    WIN_TITLES.add_object(app_label,label,**kwargs)

    #BUTTONS.add_object(app_label,label,**kwargs)
    #FORMS.add_object(app_label,label,**kwargs)
    #SECTIONS[label+"_list"]=label+"_list"
