from pymongo import MongoClient

class MongoConnector():
    """ database connector class """
    def __init__(self,server,db_name):
        self.server=server
        self.database_name=db_name
        self.database=None
        
        try:
            client = MongoClient(self.server)
        except:
            print("database server not working")
            
        self.database=client[self.database_name]
    
    def get_collection(self,collection_name):
        "return the collection the "
        collection = self.database[collection_name]
        return collection
    
    def get_number_of_post(self,collection):
        return collection.count_documents({})

    def insert_posts(self,collection,post):
        collection.insert_many(post)
        print("data successfully inserted")
        
        
        