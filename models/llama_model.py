import ollama
import re
from services.database_service import save_user_roadmap, get_user_roadmap, save_quiz_results

class LlamaRoadmapManager:
    def __init__(self, username, role, current_stage, field_of_study, end_goal):
        self.username = username
        self.role = role
        self.current_stage = current_stage
        self.field_of_study = field_of_study
        self.end_goal = end_goal

    def generate_and_save_roadmap(self):
        prompt = f'''
        Create a detailed learning roadmap in JSON format for a user with the following profile:
        - Username: {self.username}
        - Role: {self.role} (Student/Professional)
        - Current Stage: {self.current_stage}
        - Field of Study/Job Role: {self.field_of_study}
        - End Goal: {self.end_goal}

        The roadmap should include 4 phases, with each phase containing milestones, descriptions, timelines, and resources. Please format the response strictly in this JSON structure:
        {{
            "roadmap": {{
                "phases": [
                    {{
                        "name": "Phase 1: Beginner",
                        "milestones": [
                            {{
                                "name": "Milestone 1.1",
                                "description": "Learn basic concepts.",
                                "timeline": "2 weeks",
                                "resources": [ "Resource 1", "Resource 2" ]
                            }}
                        ]
                    }},
                    {{
                        "name": "Phase 2: Intermediate",
                        "milestones": [
                            {{
                                "name": "Milestone 2.1",
                                "description": "Learn intermediate concepts.",
                                "timeline": "3 weeks",
                                "resources": [ "Resource 1", "Resource 2" ]
                            }}
                        ]
                    }},
                    {{
                        "name": "Phase 3: Advanced",
                        "milestones": [
                            {{
                                "name": "Milestone 3.1",
                                "description": "Master advanced topics.",
                                "timeline": "4 weeks",
                                "resources": [ "Resource 1", "Resource 2" ]
                            }}
                        ]
                    }},
                    {{
                        "name": "Phase 4: Final",
                        "milestones": [
                            {{
                                "name": "Milestone 4.1",
                                "description": "Apply your knowledge to a real-world project.",
                                "timeline": "4 weeks",
                                "resources": [ "Resource 1", "Resource 2" ]
                            }}
                        ]
                    }}
                ]
            }}
        }}
        '''
        response = ollama.generate(model="llama3.1", prompt=prompt)
        roadmap_json = self.extract_json_from_response(response)
        save_user_roadmap(self.username, roadmap_json)
        return roadmap_json

    def extract_json_from_response(self, response):
        match = re.search(r'```json(.*?)```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            raise TypeError(f"Unexpected response format from Llama3.1: {response}")

    def get_or_generate_roadmap(self):
        roadmap = get_user_roadmap(self.username)
        if not roadmap:
            return self.generate_and_save_roadmap()
        return roadmap

    def generate_quiz(self, phase):
        prompt = f'''
        Generate a 10-question quiz in JSON format for the phase: {phase} of the following user:
        - Username: {self.username}
        - Role: {self.role} (Student/Professional)
        - Current Stage: {self.current_stage}
        - Field of Study/Job Role: {self.field_of_study}
        - End Goal: {self.end_goal}

        Please include multiple-choice, true/false, and short-answer questions. Format the response strictly in this JSON structure:
        {{
            "quiz": [
                {{
                    "question": "What is ...?",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "answer": "Option 1"
                }},
                {{
                    "question": "True or False: ...?",
                    "answer": "True"
                }},
                {{
                    "question": "Explain ... in a few sentences.",
                    "answer": "..."
                }}
            ]
        }}
        '''
        response = ollama.generate(model="llama3.1", prompt=prompt)
        return self.extract_json_from_response(response)

    def generate_gap_analysis(self, wrong_answers):
        prompt = f'''
        Provide a detailed gap analysis and feedback in JSON format based on these wrong answers: {wrong_answers} for the user with the following profile:
        - Username: {self.username}
        - Role: {self.role} (Student/Professional)
        - Current Stage: {self.current_stage}
        - Field of Study/Job Role: {self.field_of_study}
        - End Goal: {self.end_goal}

        Format:
        {{
            "gap_analysis": {{
                "recommendations": [
                    "Revise concept X",
                    "Take course Y",
                    "Watch tutorial Z"
                ]
            }}
        }}
        '''
        response = ollama.generate(model="llama3.1", prompt=prompt)
        return self.extract_json_from_response(response)