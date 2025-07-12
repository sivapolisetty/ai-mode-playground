"""
Seeder service for loading FAQ and business rules into Qdrant vector database
"""
import json
import asyncio
import os
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

class QdrantSeeder:
    """Seeder class for loading knowledge base into Qdrant"""
    
    def __init__(self, 
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Qdrant seeder
        
        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            embedding_model: SentenceTransformer model for embeddings
        """
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.embedding_model_name = embedding_model
        
        # Initialize Qdrant client
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Collection names
        self.faq_collection = "ecommerce_faq"
        self.business_rules_collection = "ecommerce_business_rules"
        
        # Get embedding dimension
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    async def create_collections(self):
        """Create Qdrant collections for FAQ and business rules"""
        logger.info("Creating Qdrant collections...")
        
        # Create FAQ collection
        try:
            self.client.create_collection(
                collection_name=self.faq_collection,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.faq_collection}")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Collection {self.faq_collection} already exists")
            else:
                logger.error(f"Error creating FAQ collection: {e}")
                raise
        
        # Create business rules collection
        try:
            self.client.create_collection(
                collection_name=self.business_rules_collection,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.business_rules_collection}")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Collection {self.business_rules_collection} already exists")
            else:
                logger.error(f"Error creating business rules collection: {e}")
                raise
    
    def load_json_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} items from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        logger.info(f"Creating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    async def seed_faq_data(self, faq_file_path: str):
        """Seed FAQ data into Qdrant"""
        logger.info("Seeding FAQ data...")
        
        # Load FAQ data
        faq_data = self.load_json_data(faq_file_path)
        
        # Prepare texts for embedding
        texts = []
        points = []
        
        for faq in faq_data:
            # Combine question and answer for better semantic search
            combined_text = f"Question: {faq['question']} Answer: {faq['answer']}"
            texts.append(combined_text)
            
            # Also add tags for better matching
            if faq.get('tags'):
                tag_text = f"Tags: {', '.join(faq['tags'])}"
                texts.append(tag_text)
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create points for insertion
        point_id = 0
        for i, faq in enumerate(faq_data):
            # Main FAQ point
            combined_text = f"Question: {faq['question']} Answer: {faq['answer']}"
            
            point = PointStruct(
                id=point_id,
                vector=embeddings[point_id],
                payload={
                    "type": "faq",
                    "id": faq["id"],
                    "category": faq["category"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "tags": faq.get("tags", []),
                    "metadata": faq.get("metadata", {}),
                    "text": combined_text
                }
            )
            points.append(point)
            point_id += 1
            
            # Add tags as separate searchable points
            if faq.get('tags'):
                tag_text = f"Tags: {', '.join(faq['tags'])}"
                tag_point = PointStruct(
                    id=point_id,
                    vector=embeddings[point_id],
                    payload={
                        "type": "faq_tags",
                        "id": faq["id"],
                        "category": faq["category"],
                        "question": faq["question"],
                        "answer": faq["answer"],
                        "tags": faq.get("tags", []),
                        "metadata": faq.get("metadata", {}),
                        "text": tag_text
                    }
                )
                points.append(tag_point)
                point_id += 1
        
        # Insert points into Qdrant
        self.client.upsert(
            collection_name=self.faq_collection,
            points=points
        )
        
        logger.info(f"Seeded {len(points)} FAQ points into Qdrant")
    
    async def seed_business_rules_data(self, rules_file_path: str):
        """Seed business rules data into Qdrant"""
        logger.info("Seeding business rules data...")
        
        # Load business rules data
        rules_data = self.load_json_data(rules_file_path)
        
        # Prepare texts for embedding
        texts = []
        points = []
        
        for rule in rules_data:
            # Create searchable text from rule - now using business-friendly format
            rule_text = f"Rule: {rule['title']} Category: {rule['category']} Description: {rule['description']}"
            
            # Add keywords to text for better matching
            if rule.get('keywords'):
                keywords_text = ', '.join(rule['keywords'])
                rule_text += f" Keywords: {keywords_text}"
            
            # Add applies_to information
            if rule.get('applies_to'):
                rule_text += f" Applies to: {rule['applies_to']}"
            
            # Add exceptions
            if rule.get('exceptions'):
                rule_text += f" Exceptions: {rule['exceptions']}"
            
            texts.append(rule_text)
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Create points for insertion
        for i, rule in enumerate(rules_data):
            point = PointStruct(
                id=i,
                vector=embeddings[i],
                payload={
                    "type": "business_rule",
                    "id": rule["id"],
                    "category": rule["category"],
                    "title": rule["title"],
                    "description": rule["description"],
                    "keywords": rule.get("keywords", []),
                    "applies_to": rule.get("applies_to", ""),
                    "exceptions": rule.get("exceptions", ""),
                    "effective_date": rule.get("effective_date", ""),
                    "last_updated": rule.get("last_updated", ""),
                    "created_by": rule.get("created_by", ""),
                    "active": rule.get("active", True),
                    "text": texts[i]
                }
            )
            points.append(point)
        
        # Insert points into Qdrant
        self.client.upsert(
            collection_name=self.business_rules_collection,
            points=points
        )
        
        logger.info(f"Seeded {len(points)} business rule points into Qdrant")
    
    async def verify_data(self):
        """Verify that data was loaded correctly"""
        logger.info("Verifying seeded data...")
        
        # Check FAQ collection
        faq_info = self.client.get_collection(self.faq_collection)
        logger.info(f"FAQ collection points: {faq_info.points_count}")
        
        # Check business rules collection
        rules_info = self.client.get_collection(self.business_rules_collection)
        logger.info(f"Business rules collection points: {rules_info.points_count}")
        
        # Test search in FAQ
        test_embedding = self.embedding_model.encode(["What is your return policy?"])
        faq_results = self.client.search(
            collection_name=self.faq_collection,
            query_vector=test_embedding[0].tolist(),
            limit=3
        )
        
        logger.info(f"FAQ search test results: {len(faq_results)} matches")
        for result in faq_results:
            logger.info(f"  - {result.payload['question'][:50]}... (score: {result.score})")
        
        # Test search in business rules
        rules_results = self.client.search(
            collection_name=self.business_rules_collection,
            query_vector=test_embedding[0].tolist(),
            limit=3
        )
        
        logger.info(f"Business rules search test results: {len(rules_results)} matches")
        for result in rules_results:
            logger.info(f"  - {result.payload['title'][:50]}... (score: {result.score})")
    
    async def clear_collections(self):
        """Clear all collections (for testing/resetting)"""
        logger.warning("Clearing all collections...")
        
        try:
            self.client.delete_collection(self.faq_collection)
            logger.info(f"Deleted collection: {self.faq_collection}")
        except Exception as e:
            logger.warning(f"Could not delete FAQ collection: {e}")
        
        try:
            self.client.delete_collection(self.business_rules_collection)
            logger.info(f"Deleted collection: {self.business_rules_collection}")
        except Exception as e:
            logger.warning(f"Could not delete business rules collection: {e}")
    
    async def run_seeding(self, knowledge_dir: str, reset: bool = False):
        """Run the complete seeding process"""
        logger.info("Starting Qdrant seeding process...")
        
        # Clear collections if reset requested
        if reset:
            await self.clear_collections()
        
        # Create collections
        await self.create_collections()
        
        # Seed FAQ data
        faq_file = os.path.join(knowledge_dir, "faq.json")
        if os.path.exists(faq_file):
            await self.seed_faq_data(faq_file)
        else:
            logger.warning(f"FAQ file not found: {faq_file}")
        
        # Seed business rules data
        rules_file = os.path.join(knowledge_dir, "business_rules.json")
        if os.path.exists(rules_file):
            await self.seed_business_rules_data(rules_file)
        else:
            logger.warning(f"Business rules file not found: {rules_file}")
        
        # Verify data
        await self.verify_data()
        
        logger.info("Seeding process completed successfully!")

async def main():
    """Main function to run the seeder"""
    # Configuration
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Knowledge directory
    current_dir = Path(__file__).parent
    knowledge_dir = current_dir.parent / "knowledge"
    
    # Initialize seeder
    seeder = QdrantSeeder(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        embedding_model=embedding_model
    )
    
    # Run seeding
    reset = "--reset" in os.sys.argv
    await seeder.run_seeding(str(knowledge_dir), reset=reset)

if __name__ == "__main__":
    asyncio.run(main())