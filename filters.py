import json


def smart_applicant_filter(payload: str):
#     system_prompt = """
# You are a summarizer system that produces required skills based on the job description provided, the output must be a JSON object that has the keys required_skills array of strings. Don't add "json" string. Don't provide an explanation, it just has to be JSON, please.
# 
# """
#     user_prompt = """
# # Job Description
# {}
# """.format(payload)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    return {"required_skills": []}  # Hanya contoh

def smart_job_filter(payload: str):
#     system_prompt = """
# You are a system that extracts required skills from the resume provided by the user. The output must be a JSON object with a single key "required_skills", containing an array of unique strings. Ensure that the output is strictly in JSON format without any additional code formatting like "json". Do not duplicate any skills.
# """
#     user_prompt = """
# # User Data 
# {}
# """.format(payload)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    return {"required_skills": []}  # Hanya contoh

def smart_recommendation_skill(user_resume: str, job_desc: str):
#     system_prompt = """Analyze a given user resume and job description to identify key skills and requirements. Based on this analysis, generate a list of recommended skills that the candidate should consider developing or acquiring to increase their chances of securing the job. Prioritize recommendations based on the job's specific requirements and the candidate's current skill set. Output the results in a JSON format with a key named "recommended_skills" containing a list of strings representing the recommended skills."""
#
#     user_prompt = """# User Resume
# {}
#
# Job Description
# {}
# 
# Output:
# """.format(user_resume, job_desc)
# 
#     messages = [
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#     ]
# 
#     inputs = tokenizer(
#     [
#       tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     ], return_tensors="pt", add_special_tokens=False).to("cuda")
# 
#     outputs = model.generate(**inputs, use_cache=True, max_new_tokens=1024)
#     outputs_str = tokenizer.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0]
# 
#     return json.loads(outputs_str)
    return {"recommended_skills": []}  # Hanya contoh