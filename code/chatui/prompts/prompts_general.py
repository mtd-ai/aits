


extract_requirements_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You have to read the given specification document, and extract a list of requirements for the project mentioned in the document. Your response format is non-negotiable: you must return a list of strings. If you cannot find any, return an empty list.
  {documents}<|end|>
  <|assistant|>
"""

feedback_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You are given a list of requirements and a document. You have to read the document and the requirements carefully. Then you have to give feedback, and assign a score to each requirement based on the information you find in the document. If the document isn't related to the requirement at all or demonstrates poor understanding of the requirement, you should score it 1. If the document satisfies the requirement and provides further information about the requirement, you should score it 10. Your response format is non-negotiable: you must return a list of JSON objects, each has 3 keys: 'requirement', 'feedback' and 'score'. The 'requirement' and 'feedback' values are strings, the 'score' value is an integer.
  Here are the requirements:
  {requirements}
  Here is the document:
  {document}<|end|>
  <|assistant|>
"""

