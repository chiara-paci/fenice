from django.urls import reverse

class GetUrl(object):
    def __init__(self,object_list=[],other_urls=[]):
        self.named_urls={}

        for app,label_list in object_list:
            self.named_urls[app+"_root"]=app+":root"
            for label in label_list:
                self.named_urls[label+"_list"]   = app+":"+label+"_list"
                self.named_urls[label+"_create"] = app+":"+label+"_list"
                self.named_urls[label+"_detail"] = app+":"+label+"_detail"
                self.named_urls[label+"_update"] = app+":"+label+"_update"
                self.named_urls[label+"_delete"] = app+":"+label+"_delete"
                
        for key,val in other_urls:
            self.named_urls[key]=val

    def __call__(self,label,*args,**kwargs):
        ret=reverse(self.named_urls[label],args=args,kwargs=kwargs)
        return ret
