
# Retrieve requirements from vector store
retrieve_requirements_prompt = """
  What are the specification, requirements, criteria, and marking scheme for this assignment?
"""

# Get requirements from retrieved related requirements chunk
extract_requirements_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You have to read the given assignment specification document, and extract a list of marking requirements for the assignment.
  Your response format is non-negotiable: you must return a list of parsable strings. If you cannot find any, return an empty list. Strings must be placed between " and ". Please put your reponse between [ and ].
  I repeat, your response format is non-negotiable: you must return a single list of strings. Strings must be placed between \" and \". Please put your reponse between [ and ].
  Here is the document:
  {documents}<|end|>
  <|assistant|>
"""

# Extract list of requirements from documents
extract_requirements_prompt_multiple = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You have to read the given assignment specification documents, and extract a list of marking requirements for all the assignments. 
  Your response format is non-negotiable: you must return a list of marking requirements. If you cannot find any, return an empty list. Please put your reponse between [ and ].
  I repeat, your response format is non-negotiable: you must return a single list of marking requirements. Do not return anything else. Please put your reponse between [ and ].
  Here is the document:
  {documents}<|end|>
  <|assistant|>
"""

# Summarization prompts. Recursive approach
first_summarize_prompt = """
  <|system|>
  You are a helpful AI assistant for summarization task.<|end|>
  <|user|>
  You have to read the given student's assignment and list the key sections of the assignment. Then you have to give a brief summary of each sections. If you find the document incomplete, just summarize what you have read. 
  Your response format is non-negotiable: you must return a list of JSON objects, each object has a 'sectionHeader' key and a 'summary' key. The 'section' and the 'summary' values are strings.
  I repeat, your response format is non-negotiable: you must return a list of JSON objects. Do not return anything else.
  Here is the assignment:
  {document}<|end|>
  <|assistant|>
"""

next_summarize_prompt = """
  <|system|>
  You are a helpful AI assistant for summarization task.<|end|>
  <|user|>
  You are given a list of JSON objects with 'sectionHeader' and 'summary' of the previous text, and a new student's assignment document. You have to read the document, identify the key sections, and give a brief summary of each section. 
  Your response format is non-negotiable: you must add a new list of JSON objects to the old list. Each object must have a 'sectionHeader' key and a 'summary' key. The 'section' value is a string representing the section header, and the 'summary' value is either a string representing the summary of the section or a list of smaller JSON objects, each represent a sub-section.
  I repeat, your response format is non-negotiable: you must return a list of JSON objects. Do not return anything else.
  Here is the JSON object contains previous sections and summaries:
  {previous}.
  Here is the current section:
  {document}<|end|>
  <|assistant|>
"""

# Feedback prompt
feedback_prompt = """
  <|system|>
  You are an insightful and detail-oriented AI assistant.<|end|>
  <|user|>
  You are provided with a list of marking requirements and a student's assignment. Your task is to carefully review the student's work, compare with the requirements, give constructive feedback, and assign a score for each marking requirement. 

  - For each requirement, provide feedback that is clear, concise, and specific to the student's understanding and performance.
  - If the assignment does not address a marking requirement at all or shows minimal understanding, you should assign a score of 1 for that requirement.
  - If the assignment satisfies the marking requirement and provides further information about the marking requirement topic, you assign a score of 10 for that requirement.
  
  Your response format is non-negotiable: you must return a list of JSON objects, where each object includes the following:
  - 'requirement': The marking requirement being assessed.
  - 'feedback': A paragraph comparing the requirements and what the student did, comment whether the student met the requirement or not.
  - 'score': An integer value between 1 and 10 that reflects how well the student satisfied that specific requirement.

  I repeat, your response format is non-negotiable: you must return a list of JSON objects. Please put your reponse between [ and ]. 

  Here are the marking requirements:
  {criteria}

  Here is the student's assignment:
  {document}<|end|>
  <|assistant|>
"""

# Read email and find related files
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


generate_response_email_prompt = """
  <|system|>
  You are a helpful AI assistant who write response emails to students.<|end|>
  <|user|>
  You are given an email from a student and a feedback draft. You have to format the feedback into a response email to the student. Your response format is non-negotiable: you must return a string. Do not add any additional information. Do not remove any information.
  Here is the student's email:
  {email}
  Here is the feedback draft:
  {feedback}<|end|>
  <|assistant|>
"""