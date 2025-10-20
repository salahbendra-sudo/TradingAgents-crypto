import chromadb
from chromadb.config import Settings
from openai import OpenAI


class FinancialSituationMemory:
    def __init__(self, name, config):
        # Determine embedding model based on provider
        if config["backend_url"] == "http://localhost:11434/v1":
            self.embedding = "nomic-embed-text"
            self.client = OpenAI(
                base_url=config["backend_url"],
                api_key=config["api_key"]
            )
        elif "deepseek" in config.get("llm_provider", "").lower():
            # DeepSeek doesn't support embeddings, use local model
            self.embedding = "local"
            self.client = None
            self._setup_local_embeddings()
        else:
            self.embedding = "text-embedding-3-small"
            self.client = OpenAI(
                base_url=config["backend_url"],
                api_key=config["api_key"]
            )
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        
        # Make collection name unique per session to avoid conflicts
        session_id = config.get('session_id', 'default')
        unique_name = f"{name}_{session_id}"
        
        # Check if collection already exists, if so delete it and create new one
        try:
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            if unique_name in existing_collections:
                self.chroma_client.delete_collection(name=unique_name)
        except Exception as e:
            # If there's any issue checking/deleting, just continue
            pass
        
        # Create the collection (now guaranteed to be fresh and unique)
        self.situation_collection = self.chroma_client.create_collection(name=unique_name)

    def _setup_local_embeddings(self):
        """Setup local embedding model for DeepSeek"""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            # Use a small, efficient model
            model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_model = AutoModel.from_pretrained(model_name)
            self.local_torch = torch  # Store torch reference
            print(f"[DEBUG] Local embedding model loaded: {model_name}")
        except ImportError:
            print("[WARNING] transformers not available, falling back to dummy embeddings")
            self.local_tokenizer = None
            self.local_model = None
            self.local_torch = None
        except Exception as e:
            print(f"[WARNING] Failed to load local embedding model: {e}")
            self.local_tokenizer = None
            self.local_model = None
            self.local_torch = None

    def get_embedding(self, text):
        """Get embedding for a text"""
        
        if self.embedding == "local":
            # Use local embedding model
            if hasattr(self, 'local_model') and self.local_model is not None:
                return self._get_local_embedding(text)
            else:
                # Fallback to dummy embeddings if local model failed to load
                return [0.0] * 384
        
        response = self.client.embeddings.create(
            model=self.embedding, input=text
        )
        return response.data[0].embedding

    def _get_local_embedding(self, text):
        """Get embedding using local model"""
        try:
            inputs = self.local_tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
            with self.local_torch.no_grad():
                outputs = self.local_model(**inputs)
            # Mean pooling
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings[0].numpy().tolist()
        except Exception as e:
            print(f"[WARNING] Error in local embedding: {e}")
            # Fallback to dummy embeddings
            return [0.0] * 384

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
