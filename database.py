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

    def create_id(self, id: int):
        self.create({"_id": id})

    def update(self, key, value, upsert=True):
        self.col.update_one(key, {"$set": value}, upsert=upsert)

    def update_id(self, id: int, value, upsert=True):
        self.update({"_id": id}, value, upsert=upsert)

    def reset_id(self, id: int):
        self.col.delete_one({"_id": id})
        self.create_id(id)

    def delete_id(self, id: int):
        self.col.delete_one({"_id": id})

    # Check if entry with _id exists
    def exists_id(self, id: int):
        return self.col.count_documents({"_id": id}) >= 1