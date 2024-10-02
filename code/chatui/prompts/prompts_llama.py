extract_requirements_prompt = """
  <|system|>
  You are a precise and diligent AI assistant.<|end|>
  <|user|>
  You are tasked with analyzing the following assignment specification document and extracting a comprehensive list of marking requirements. These requirements may include specific criteria, grading rubrics, or expectations for the assignment. 
  Your output must strictly adhere to this format: 
  - A Python list containing strings, where each string represents a distinct requirement.
  - If no requirements are identified, return an empty list.
  
  Ensure the list is exhaustive and relevant to the assignment grading process. Avoid adding any interpretations or assumptions beyond the document's content.\
  Here is the document:
  {documents}<|end|>
  <|assistant|>
"""