

retrieve_requirements_prompt = """
  What are the specification, requirements, criteria, and marking scheme for this assignment?
"""


extract_requirements_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You have to read the given assignment specification document, and extract a list of marking requirements for the assignment. Your response format is non-negotiable: you must return a list of strings. If you cannot find any, return an empty list.
  {documents}<|end|>
  <|assistant|>
"""

mark_requirements_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You are given a list of marking requirements. You have to read the given student's assignment and give an integer score between 1 to 10 for each marking requirements.
"""

first_summarize_prompt = """
  <|system|>
  You are a helpful AI assistant for summarization task.<|end|>
  <|user|>
  You have to read the given student's assignment and list the key sections of the assignment. Then you have to give a brief summary of each sections. If you find the document incomplete, just summarize what you have read. Your response format is non-negotiable: you must return a list of JSON objects, each object has a 'sectionHeader' key and a 'summary' key. The 'section' and the 'summary' values are strings.
  Here is the assignment:
  {document}<|end|>
  <|assistant|>
"""


next_summarize_prompt = """
  <|system|>
  You are a helpful AI assistant for summarization task.<|end|>
  <|user|>
  You are given a JSON object with key sections and summary of the previous sections, and a student's assignment section. You have to read the section and list the key sections of the assignment. Then you have to give a brief summary of each sections, and append it to the previous JSON object. Your response format is non-negotiable: you must return a list of JSON objects, each object has a 'sectionHeader' key and a 'summary' key. The 'section' value is a string representing the section header, and the 'summary' value is either a string representing the summary of the section or a list of smaller JSON objects, each represent a sub-section.
  Here is the JSON object contains previous sections and summaries:
  {previous}.
  Here is the current section:
  {document}<|end|>
  <|assistant|>
"""


feedback_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You are given a marking requirements and a student's assignment. You have to read the student's assignment, give feedback, and assign a score to the student assignment based on the marking requirements. If the assignment isn't related to the marking requirement at all or demonstrates poor understanding of the marking requirements, you should score it 1. If the assignment satisfies the marking requirement and provides further information about the marking requirement topic, you should score it 10. Your response format is non-negotiable: you must return a list of JSON objects, each has 3 keys: 'requirement', 'feedback' and 'score'. The 'requirement' and 'feedback' values are strings, the 'score' value is an integer.
  Here is the marking criteria:
  {criteria}
  Here is the student's assignment:
  {document}<|end|>
  <|assistant|>
"""


find_related_files_from_email_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You are given an email from a student and a list of files names. You have to read the email, find the related files, and return the information. Your response format is non-negotiable: you must return a JSON object with 5 fields: 'sender', 'email_address', 'title', 'content', 'related_files'. The 'sender', 'title', 'content' values are strings, the 'related_files' value is a list of strings. If you cannot find any related files, you can return an empty string for the 'related_files' value. For other fields, you can return a blank string if you cannot find the information in the email. 
  Here is the email:
  {email}
  Here is the list of files:
  {files}<|end|>
  <|assistant|>
"""

find_related_files_from_emails_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You are given a list of emails from a student and a list of files names. You have to read the emails and return information about each email. Your response format is non-negotiable: you must return a list of JSON objects, each JSON object correspond to an email you find. Each JSON object has 5 fields: 'sender', 'email_address', 'title', 'content', 'related_files'. The 'sender', 'title', 'content' values are strings, the 'related_files' value is a list of file names. You can return an empty list if you cannot find any emails. If you cannot find any related files, you can return an empty string for the 'related_files' value. For the 'sender', 'email_address', 'title', and 'content' fields, you can return a blank string if you cannot find the information in the email.
  Here are the emails:
  {emails}
  Here is the list of files:
  {files}<|end|>
  <|assistant|>
"""