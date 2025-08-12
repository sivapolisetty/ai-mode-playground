"""
RAG Service for semantic search and knowledge retrieval from Qdrant
"""
import os
import sys
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ai_backend.shared.observability.langfuse_decorator import trace_rag_operation, observe
except ImportError:
    # Fallback no-op decorator if import fails
    def trace_rag_operation(collection_type: str = "unknown"):
        def decorator(func):
            return func
        return decorator
    
    def observe(as_type: str = "span", **kwargs):
        def decorator(func):
            return func
        return decorator

# Load environment variables
load_dotenv()

class QueryType(Enum):
    """Types of queries that can be processed"""
    FAQ = "faq"
    BUSINESS_RULE = "business_rule"
    TRANSACTIONAL = "transactional"
    MIXED = "mixed"

@dataclass
class SearchResult:
    """Result from vector search"""
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    type: str

@dataclass
class RAGResponse:
    """Response from RAG service"""
    query: str
    query_type: QueryType
    results: List[SearchResult]
    context: str
    confidence: float
    sources: List[str]

class RAGService:
    """RAG service for semantic search and knowledge retrieval"""
    
    def __init__(self, 
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG service
        
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
        
        # Search parameters
        self.default_limit = 5
        self.confidence_threshold = 0.3
        
        # Query classification keywords
        self.faq_keywords = {
            "shipping", "delivery", "return", "refund", "policy", "warranty",
            "payment", "account", "password", "login", "support", "contact",
            "hours", "discount", "coupon", "loyalty", "rewards", "security"
        }
        
        self.transactional_keywords = {
            "buy", "purchase", "order", "cart", "checkout", "product", "search",
            "find", "show", "get", "list", "customer", "price", "inventory",
            "stock", "category", "brand", "model"
        }
        
        self.business_rule_keywords = {
            "rule", "policy", "condition", "if", "when", "then", "discount",
            "promotion", "eligibility", "qualification", "threshold", "limit"
        }
    
    @observe(as_type="span")
    async def classify_query(self, query: str) -> QueryType:
        """
        Classify query type based on keywords and context
        
        Args:
            query: User query to classify
            
        Returns:
            QueryType: Classified query type
        """
        query_lower = query.lower()
        
        # Count keyword matches
        faq_matches = sum(1 for keyword in self.faq_keywords if keyword in query_lower)
        transactional_matches = sum(1 for keyword in self.transactional_keywords if keyword in query_lower)
        business_rule_matches = sum(1 for keyword in self.business_rule_keywords if keyword in query_lower)
        
        # Classification logic
        if faq_matches > 0 and transactional_matches > 0:
            return QueryType.MIXED
        elif faq_matches >= transactional_matches and faq_matches >= business_rule_matches:
            return QueryType.FAQ
        elif business_rule_matches > 0:
            return QueryType.BUSINESS_RULE
        else:
            return QueryType.TRANSACTIONAL
    
    @observe(as_type="span")
    async def search_faq(self, query: str, limit: int = None) -> List[SearchResult]:
        """
        Search FAQ knowledge base
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        limit = limit or self.default_limit
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in FAQ collection
        results = self.client.search(
            collection_name=self.faq_collection,
            query_vector=query_embedding[0].tolist(),
            limit=limit,
            score_threshold=self.confidence_threshold
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            search_result = SearchResult(
                id=result.payload.get("id", ""),
                score=result.score,
                content=result.payload.get("answer", ""),
                metadata={
                    "question": result.payload.get("question", ""),
                    "category": result.payload.get("category", ""),
                    "tags": result.payload.get("tags", []),
                    "source": "FAQ"
                },
                type="faq"
            )
            search_results.append(search_result)
        
        logger.info(f"FAQ search returned {len(search_results)} results")
        return search_results
    
    @observe(as_type="span")
    async def search_business_rules(self, query: str, limit: int = None) -> List[SearchResult]:
        """
        Search business rules knowledge base
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        limit = limit or self.default_limit
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in business rules collection
        results = self.client.search(
            collection_name=self.business_rules_collection,
            query_vector=query_embedding[0].tolist(),
            limit=limit,
            score_threshold=self.confidence_threshold
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            search_result = SearchResult(
                id=result.payload.get("id", ""),
                score=result.score,
                content=result.payload.get("description", ""),
                metadata={
                    "title": result.payload.get("title", ""),
                    "category": result.payload.get("category", ""),
                    "keywords": result.payload.get("keywords", []),
                    "applies_to": result.payload.get("applies_to", ""),
                    "exceptions": result.payload.get("exceptions", ""),
                    "effective_date": result.payload.get("effective_date", ""),
                    "created_by": result.payload.get("created_by", ""),
                    "active": result.payload.get("active", True),
                    "source": "Business Rules"
                },
                type="business_rule"
            )
            search_results.append(search_result)
        
        logger.info(f"Business rules search returned {len(search_results)} results")
        return search_results
    
    async def search_by_category(self, query: str, category: str, collection_type: str = "faq") -> List[SearchResult]:
        """
        Search within a specific category
        
        Args:
            query: Search query
            category: Category to filter by
            collection_type: Type of collection (faq or business_rules)
            
        Returns:
            List of search results
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Create category filter
        category_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category)
                )
            ]
        )
        
        # Choose collection
        collection_name = self.faq_collection if collection_type == "faq" else self.business_rules_collection
        
        # Search with filter
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding[0].tolist(),
            limit=self.default_limit,
            query_filter=category_filter,
            score_threshold=self.confidence_threshold
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            if collection_type == "faq":
                search_result = SearchResult(
                    id=result.payload.get("id", ""),
                    score=result.score,
                    content=result.payload.get("answer", ""),
                    metadata={
                        "question": result.payload.get("question", ""),
                        "category": result.payload.get("category", ""),
                        "tags": result.payload.get("tags", []),
                        "source": "FAQ"
                    },
                    type="faq"
                )
            else:
                search_result = SearchResult(
                    id=result.payload.get("id", ""),
                    score=result.score,
                    content=result.payload.get("description", ""),
                    metadata={
                        "title": result.payload.get("title", ""),
                        "category": result.payload.get("category", ""),
                        "keywords": result.payload.get("keywords", []),
                        "applies_to": result.payload.get("applies_to", ""),
                        "exceptions": result.payload.get("exceptions", ""),
                        "effective_date": result.payload.get("effective_date", ""),
                        "created_by": result.payload.get("created_by", ""),
                        "active": result.payload.get("active", True),
                        "source": "Business Rules"
                    },
                    type="business_rule"
                )
            
            search_results.append(search_result)
        
        logger.info(f"Category search ({category}) returned {len(search_results)} results")
        return search_results
    
    @observe(as_type="span")
    async def hybrid_search(self, query: str, limit: int = None) -> List[SearchResult]:
        """
        Perform hybrid search across both FAQ and business rules
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Combined and ranked search results
        """
        limit = limit or self.default_limit
        
        # Search both collections
        faq_results = await self.search_faq(query, limit=limit//2 + 1)
        rule_results = await self.search_business_rules(query, limit=limit//2 + 1)
        
        # Combine results
        all_results = faq_results + rule_results
        
        # Sort by score (descending)
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top results
        return all_results[:limit]
    
    @trace_rag_operation("hybrid")
    @observe(as_type="span")
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> RAGResponse:
        """
        Process a query and return RAG response
        
        Args:
            query: User query
            context: Additional context information
            
        Returns:
            RAGResponse with results and context
        """
        logger.info(f"Processing RAG query: {query}")
        
        # Classify query
        query_type = await self.classify_query(query)
        logger.info(f"Query classified as: {query_type.value}")
        
        # Search based on query type
        if query_type == QueryType.FAQ:
            results = await self.search_faq(query)
        elif query_type == QueryType.BUSINESS_RULE:
            results = await self.search_business_rules(query)
        elif query_type == QueryType.MIXED:
            results = await self.hybrid_search(query)
        else:
            # For transactional queries, return empty results
            results = []
        
        # Build context from results
        context_parts = []
        sources = []
        
        for result in results:
            if result.type == "faq":
                context_parts.append(f"Q: {result.metadata['question']}\nA: {result.content}")
                sources.append(f"FAQ - {result.metadata['category']}")
            elif result.type == "business_rule":
                context_parts.append(f"Rule: {result.metadata['title']}\nDescription: {result.content}")
                sources.append(f"Business Rule - {result.metadata['category']}")
        
        # Calculate overall confidence
        if results:
            confidence = sum(r.score for r in results) / len(results)
        else:
            confidence = 0.0
        
        # Build response
        response = RAGResponse(
            query=query,
            query_type=query_type,
            results=results,
            context="\n\n".join(context_parts),
            confidence=confidence,
            sources=sources
        )
        
        logger.info(f"RAG response generated with {len(results)} results, confidence: {confidence:.2f}")
        return response
    
    @observe(as_type="span")
    async def get_similar_questions(self, query: str, limit: int = 3) -> List[str]:
        """
        Get similar questions from FAQ for query suggestions
        
        Args:
            query: User query
            limit: Number of suggestions
            
        Returns:
            List of similar questions
        """
        # Search FAQ
        results = await self.search_faq(query, limit=limit)
        
        # Extract questions
        questions = []
        for result in results:
            if result.metadata.get("question"):
                questions.append(result.metadata["question"])
        
        return questions
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the RAG service
        
        Returns:
            Health status information
        """
        try:
            # Check Qdrant connection
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            # Check if required collections exist
            faq_exists = self.faq_collection in collection_names
            rules_exists = self.business_rules_collection in collection_names
            
            # Get collection stats
            stats = {}
            if faq_exists:
                faq_info = self.client.get_collection(self.faq_collection)
                stats["faq_points"] = faq_info.points_count
            
            if rules_exists:
                rules_info = self.client.get_collection(self.business_rules_collection)
                stats["business_rules_points"] = rules_info.points_count
            
            return {
                "status": "healthy",
                "qdrant_connected": True,
                "collections": {
                    "faq_exists": faq_exists,
                    "business_rules_exists": rules_exists
                },
                "stats": stats,
                "embedding_model": self.embedding_model_name
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "qdrant_connected": False
            }

async def main():
    """Test the RAG service"""
    # Initialize service
    rag_service = RAGService()
    
    # Test queries
    test_queries = [
        "What is your return policy?",
        "How do I track my order?",
        "What payment methods do you accept?",
        "Do you offer free shipping?",
        "How do I return an item?",
        "What are the business rules for discounts?",
        "Find me some laptops"  # Transactional query
    ]
    
    # Process each query
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        response = await rag_service.process_query(query)
        
        print(f"Query Type: {response.query_type.value}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Results: {len(response.results)}")
        
        if response.results:
            print(f"Context:\n{response.context}")
            print(f"Sources: {', '.join(response.sources)}")
        else:
            print("No knowledge base results - would route to transactional tools")

if __name__ == "__main__":
    asyncio.run(main())