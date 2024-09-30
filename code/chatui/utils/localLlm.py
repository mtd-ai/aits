from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline 

from pydantic import Field
from typing import Optional, Any
import torch

from typing import Any, Dict, List, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM


class Phi3LLM(LLM):

    tokenizer: Any
    model: Any
    device: Any
    pipel: Any
    generation_args: Any

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct", cache_dir="/", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
        if torch.cuda.is_available():
            self.device = torch.device("cuda")  
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")   
        else:
            self.device = torch.device("cpu")
        self.model.to(self.device)
        self.pipel = pipeline( 
            "text-generation", 
            model=self.model, 
            tokenizer=self.tokenizer, 
            device=self.device
        )
        self.generation_args = { 
            "max_new_tokens": 500, 
            "return_full_text": False, 
            "do_sample": False, 
        } 


    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        out = self.pipel(prompt, **self.generation_args)
        
        return out[0]['generated_text']
    
    @property
    def _llm_type(self) -> str:
        return "phi-3"
    
