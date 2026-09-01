import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from app.core.config import BASE_DIR, DATABASE_NAME, MONGODB_URL

logger = logging.getLogger("career_advisor.db")

class ResilientCollection:
    """In-memory & JSON file backed collection that mimics Motor/PyMongo async interface."""
    def __init__(self, name: str, store: "ResilientDB"):
        self.name = name
        self.store = store

    async def find(self, query: Optional[Dict[str, Any]] = None) -> "ResilientCursor":
        query = query or {}
        items = self.store.get_items(self.name)
        matched = []
        for item in items:
            match = True
            for k, v in query.items():
                if k == "$or" and isinstance(v, list):
                    if not any(all(item.get(qk) == qv for qk, qv in qclause.items()) for qclause in v):
                        match = False
                        break
                elif item.get(k) != v:
                    match = False
                    break
            if match:
                matched.append(dict(item))
        return ResilientCursor(matched)

    async def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        cursor = await self.find(query)
        items = await cursor.to_list(length=1)
        return items[0] if items else None

    async def insert_one(self, document: Dict[str, Any]):
        doc = dict(document)
        if "_id" not in doc and "id" not in doc:
            doc["id"] = str(uuid.uuid4())
        if "_id" not in doc:
            doc["_id"] = doc.get("id")
        self.store.insert_item(self.name, doc)
        return type("InsertResult", (), {"inserted_id": doc.get("id", doc.get("_id"))})()

    async def insert_many(self, documents: List[Dict[str, Any]]):
        for d in documents:
            await self.insert_one(d)

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        items = self.store.get_items(self.name)
        for idx, item in enumerate(items):
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                updated_doc = dict(item)
                if "$set" in update:
                    updated_doc.update(update["$set"])
                else:
                    updated_doc.update(update)
                self.store.update_item(self.name, idx, updated_doc)
                return type("UpdateResult", (), {"matched_count": 1, "modified_count": 1})()
        return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})()

    async def delete_one(self, query: Dict[str, Any]):
        items = self.store.get_items(self.name)
        for idx, item in enumerate(items):
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                self.store.delete_item(self.name, idx)
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        cursor = await self.find(query)
        items = await cursor.to_list(length=None)
        return len(items)


class ResilientCursor:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def sort(self, key_or_list, direction=1):
        if isinstance(key_or_list, str):
            reverse = direction == -1
            self.data.sort(key=lambda x: x.get(key_or_list, 0), reverse=reverse)
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is None:
            return list(self.data)
        return list(self.data[:length])

    def __aiter__(self):
        self._iter = iter(self.data)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class ResilientDB:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load local storage {self.storage_path}: {e}")
                self._data = {}
        else:
            self._data = {}

    def save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving to {self.storage_path}: {e}")

    def get_items(self, collection: str) -> List[Dict[str, Any]]:
        return self._data.setdefault(collection, [])

    def insert_item(self, collection: str, doc: Dict[str, Any]):
        self._data.setdefault(collection, []).append(doc)
        self.save()

    def update_item(self, collection: str, index: int, doc: Dict[str, Any]):
        self._data.setdefault(collection, [])[index] = doc
        self.save()

    def delete_item(self, collection: str, index: int):
        self._data.setdefault(collection, []).pop(index)
        self.save()

    def __getitem__(self, collection_name: str) -> ResilientCollection:
        return ResilientCollection(collection_name, self)


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.is_mongo = False
        self.fallback_db = ResilientDB(BASE_DIR / "sample_data" / "db_store.json")

    async def connect(self):
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=1500)
            # Check connection
            await client.admin.command("ping")
            self.client = client
            self.db = client[DATABASE_NAME]
            self.is_mongo = True
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.info(f"MongoDB not available ({e}). Using Resilient local persistence adapter.")
            self.is_mongo = False
            self.db = self.fallback_db

    def get_collection(self, name: str):
        if self.is_mongo and self.db is not None:
            return self.db[name]
        return self.fallback_db[name]


db_manager = DatabaseManager()

def get_db():
    return db_manager
