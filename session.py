class Session:
    _instance = None
    _host={}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(cls):
        cls.variable = "Soy un Singleton"
    
    def addHost(cls, host, token,link):
        cls._host[host]={"token":token,"link":link}

    def getToken(cls,host): 
        return cls._host.get(host)["token"]
    
    def getLink(cls,host):
        return cls._host.get(host)["link"]