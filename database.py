import pymongo

class Database:
    def __init__(self, collection: str):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["discord"]
        self.col = self.db[collection]
    
    def set_defaults(self, defs):
        self.defs = defs

    def read(self, key):
        return self.col.find_one(key)

    def read_id_key(self, id: int, key):
        data = self.read({"_id": id})
        if key in data:
            return data[key]
        # If does not exist, return default value
        val = self.defs[key]
        #self.update({"_id": id}, {key: val})
        return val

    def create(self, document):
        self.col.insert_one(document)

    def update(self, key, value, upsert=True):
        self.col.update_one(key, {"$set": value}, upsert=upsert)

    def delete(self, key):
        # Todo: implement this lmao
        pass