

email_prompt = """
  Instruct: You are an email assistant. You have to read the email and figure out if the email is from a student. If the email is not from a student, return 'Not a student email'. If the email is from a student, you must return a JSON object with the following schema: 
  {{
    "Email": string,
    "Name": string,
    "Student ID": string,
    "Course": string,
    "Issue": string,
  }}
  Don't repeat the question. Only return the output JSON object. If you have finished returning the JSON object, stop generating. If there are more than one match, return the first match.
  Here is the email:
  {prompt}
  Output:
"""

email_output_schema = """
  {
    "Email": string,
    "Name": string,
    "Student ID": string,
    "Course": string,
    "Issue": string,
  }
"""


retrieve_requirements_prompt = """
  What are the specification, requirements, criteria, and marking scheme for this assignment?
"""

extract_requirements_prompt = """
  Instruct:
  You are finding a list of specification, requirements, criteria, and marking scheme in a set of documents. Your response format is non-neogtiable: you must return a JSON object with a single 'results' field, and the value is a list of strings. If you cannot find any, the list should be empty. 
  Here are the documents:
  {documents}
  Output:
"""

marking_prompt = """
  Instruct:
  You are a helpful AI assistant. You have to read the marking scheme list and the student's assignment. You have to figure out if the student's assignment meets the marking scheme. You have to give each marking scheme a score from 1 to 10. You must generate a score for each marking schema, and return the list of scores.
  Here is the marking scheme list:
  {marking_scheme}
  Output:
"""

phi_3_extract_requirements_prompt = """
  <|system|>
  You are a helpful AI assistant.<|end|>
  <|user|>
  You have to read the given assignment specification document, and extract a list of marking requirements for the assignment. Your response format is non-negotiable: you must return a list of strings. If you cannot find any, return an empty list.
  {document}<|end|>
  <|assistant|>
"""


email_result_format = """
  ## Sender: 
  {sender}
  ## Email Address: 
  {email_address}
  ## Title: 
  {title}
  ## Content:
  {content}
"""


generate_response_email_prompt = """
  <|system|>
  You are a helpful AI assistant who format response to student email.<|end|>
  <|user|>
  You have to read the given student's email and a grader's feedback draft to that email. You have to format the feedback into a response email to the student. Do not add any additional information. Do not remove any information. Your response format is non-negotiable: you must return a string.
  Here is the student's email:
  {email}
  Here is the feedback draft:
  {feedback}<|end|>
  <|assistant|>
"""