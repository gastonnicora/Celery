class Session:
    _instance = None
    _host={}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(cls):
        cls.variable = "Soy un Singleton"
    
    def addHost(cls, host, token):
        cls._host[host]=token

    def getHost(cls,host):
        print(cls._host)
        return cls._host.get(host) 