import subprocess
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class CompanySearchRequest(BaseModel):
    industry: str
    location: Optional[str] = "UK"
    size_category: Optional[str] = None  # startup, sme, enterprise

class CompanySearchResponse(BaseModel):
    companies: List[Dict[str, Any]]
    search_metadata: Dict[str, Any]

class HuggingFaceService:
    """Service to interact with Hugging Face models and datasets via MCP"""
    
    def __init__(self):
        self.server_name = "hugging-face"
    
    async def search_acquisition_targets(self, request: CompanySearchRequest) -> CompanySearchResponse:
        """Search for potential acquisition targets using HF datasets"""
        
        try:
            # Search for relevant datasets that might contain company information
            search_query = f"companies {request.industry} {request.location or 'UK'} business directory"
            
            result = subprocess.run([
                "manus-mcp-cli", "tool", "call", "dataset_search",
                "--server", self.server_name,
                "--input", json.dumps({
                    "query": search_query,
                    "limit": 10,
                    "tags": ["business", "companies"]
                })
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                datasets_data = json.loads(result.stdout)
                
                # Process and format the results
                companies = []
                for dataset in datasets_data.get("datasets", []):
                    companies.append({
                        "name": dataset.get("id", "Unknown"),
                        "description": dataset.get("description", ""),
                        "tags": dataset.get("tags", []),
                        "downloads": dataset.get("downloads", 0),
                        "source": "huggingface_dataset"
                    })
                
                return CompanySearchResponse(
                    companies=companies,
                    search_metadata={
                        "query": search_query,
                        "total_results": len(companies),
                        "source": "hugging_face_datasets"
                    }
                )
            else:
                raise Exception(f"HuggingFace search failed: {result.stderr}")
                
        except Exception as e:
            # Return fallback response
            return CompanySearchResponse(
                companies=[],
                search_metadata={
                    "error": str(e),
                    "query": request.industry,
                    "total_results": 0,
                    "source": "error_fallback"
                }
            )
    
    async def find_market_research_papers(self, industry: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find relevant research papers for market analysis"""
        
        try:
            search_query = f"market analysis {industry} M&A mergers acquisitions"
            
            result = subprocess.run([
                "manus-mcp-cli", "tool", "call", "paper_search",
                "--server", self.server_name,
                "--input", json.dumps({
                    "query": search_query,
                    "results_limit": limit,
                    "concise_only": True
                })
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                papers_data = json.loads(result.stdout)
                
                papers = []
                for paper in papers_data.get("papers", []):
                    papers.append({
                        "title": paper.get("title", "Unknown"),
                        "authors": paper.get("authors", []),
                        "abstract": paper.get("abstract", ""),
                        "url": paper.get("url", ""),
                        "published": paper.get("published", ""),
                        "relevance_score": paper.get("relevance_score", 0)
                    })
                
                return papers
            else:
                raise Exception(f"Paper search failed: {result.stderr}")
                
        except Exception as e:
            return [{
                "title": "Research papers temporarily unavailable",
                "authors": ["System"],
                "abstract": f"Error: {str(e)}",
                "url": "",
                "published": "2024",
                "relevance_score": 0
            }]
    
    async def get_financial_models(self, task_type: str = "financial-analysis") -> List[Dict[str, Any]]:
        """Find relevant financial analysis models"""
        
        try:
            result = subprocess.run([
                "manus-mcp-cli", "tool", "call", "model_search",
                "--server", self.server_name,
                "--input", json.dumps({
                    "query": f"financial {task_type} valuation",
                    "task": "text-generation",
                    "limit": 5,
                    "sort": "downloads"
                })
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                models_data = json.loads(result.stdout)
                
                models = []
                for model in models_data.get("models", []):
                    models.append({
                        "id": model.get("id", ""),
                        "name": model.get("modelId", "Unknown"),
                        "description": model.get("description", ""),
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "tags": model.get("tags", []),
                        "url": f"https://huggingface.co/{model.get('modelId', '')}"
                    })
                
                return models
            else:
                raise Exception(f"Model search failed: {result.stderr}")
                
        except Exception as e:
            return [{
                "id": "error",
                "name": "Models temporarily unavailable",
                "description": f"Error: {str(e)}",
                "downloads": 0,
                "likes": 0,
                "tags": [],
                "url": ""
            }]
    
    async def generate_deal_summary_image(self, deal_name: str, key_metrics: Dict[str, Any]) -> Optional[str]:
        """Generate a visual summary of deal metrics"""
        
        try:
            # Create a prompt for deal visualization
            prompt = f"Professional business infographic showing M&A deal summary for {deal_name}, clean corporate design, charts and metrics, blue and white color scheme"
            
            result = subprocess.run([
                "manus-mcp-cli", "tool", "call", "gr1_flux1_schnell_infer",
                "--server", self.server_name,
                "--input", json.dumps({
                    "prompt": prompt,
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 8
                })
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                image_data = json.loads(result.stdout)
                return image_data.get("image_url", None)
            else:
                return None
                
        except Exception as e:
            return None

# Global service instance
huggingface_service = HuggingFaceService()
