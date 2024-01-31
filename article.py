class Articles:
    _instance = None
    _articles={}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(cls):
        cls.variable = "Soy un Singleton"
    
    def addArticle(cls, article, taskId):
        cls._articles[article]=taskId
    
    def getTaskId(cls,article):
         return cls._articles.get(article)      
