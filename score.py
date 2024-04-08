import os
import json 
from PyPDF2 import PdfReader 
from openai import OpenAI


class score_model():
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key = self.OPENAI_API_KEY)

        self.all_possible_experience_topic = ['Professional Experience',
                                                'Professional experience',
                                                'PROFESSIONAL EXPERIENCE',
                                                'Professional Experiences',
                                                'PROFESSIONAL EXPERIENCES',
                                                'Working Experience',
                                                'Working experience',
                                                'WORKING EXPERIENCE',
                                                'Working Experiences',
                                                'WORKING EXPERIENCES',
                                                'Employment Experience',
                                                'Employment experience',
                                                'EMPLOYMENT EXPERIENCE',
                                                'Employment Experiences',
                                                'EMPLOYMENT EXPERIENCES',
                                                'Work Experience',
                                                'Work experience',
                                                'WORK EXPERIENCE',
                                                'Work Experiences',
                                                'WORK EXPERIENCES',
                                                'Internship',
                                                'Internship',
                                                'INTERNSHIP',
                                                'Internships',
                                                'INTERNSHIPS',
                                                'Internship Experience',
                                                'Internship experience',
                                                'INTERNSHIP EXPERIENCE',
                                                'Internship Experiences',
                                                'INTERNSHIP EXPERIENCES']
        self.all_possible_project_topic = ['Academic Experience',
                                            'Academic experience',
                                            'ACADEMIC EXPERIENCE',
                                            'Academic Experiences',
                                            'ACADEMIC EXPERIENCES',
                                            'Research Experience',
                                            'Research experience',
                                            'RESEARCH EXPERIENCE',
                                            'Research Experiences',
                                            'RESEARCH EXPERIENCES',
                                            'Academic Project',
                                            'Academic project',
                                            'ACADEMIC PROJECT',
                                            'Academic Projects',
                                            'ACADEMIC PROJECTS',
                                            'Project',
                                            'Project',
                                            'PROJECT',
                                            'Projects',
                                            'PROJECTS',
                                            'Academic Project Experience',
                                            'Academic project experience',
                                            'ACADEMIC PROJECT EXPERIENCE',
                                            'Academic Project Experiences',
                                            'ACADEMIC PROJECT EXPERIENCES',
                                            'Research Project',
                                            'Research project',
                                            'RESEARCH PROJECT',
                                            'Research Projects',
                                            'RESEARCH PROJECTS',
                                            'Activities',
                                            'Activities',
                                            'ACTIVITIES',
                                            'Activitiess',
                                            'ACTIVITIESS',
                                            'Activity Experience',
                                            'Activity experience',
                                            'ACTIVITY EXPERIENCE',
                                            'Activity Experiences',
                                            'ACTIVITY EXPERIENCES']
        self.all_possible_skill_topic = ['Skill',
                                        'Skills and Interest',
                                        'Technical Skill',
                                        'Tech Skill',
                                        'Expertise',
                                        'Additional Information',
                                        'Tech Stack',
                                        'Skills&interests']

    def read_text(self, file_path):
        # now only deal with pdf 
        raw_text = ""
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for i in range(len(reader.pages)):
                page = reader.pages[i]

                raw_text += page.extract_text()
        return raw_text

    def get_experience_position(self, raw_text):
        work_experience_pointer = -1 
        project_experience_pointer = len(raw_text) - 1
        skill_experience_pointer = len(raw_text) - 1

        for i in self.all_possible_experience_topic:
            if i in raw_text:
                work_experience_pointer = raw_text.find(i)
                break
        for i in self.all_possible_project_topic:
            if i in raw_text:
                project_experience_pointer = raw_text.find(i)
                break
        for i in self.all_possible_skill_topic:
            if i in raw_text:
                skill_experience_pointer = raw_text.find(i)
                break
        if work_experience_pointer == -1:
            raise Exception("Couldn't find working experience")

        experience_end_pointer = min(project_experience_pointer, skill_experience_pointer)

        return work_experience_pointer, experience_end_pointer

    def openai_call(self, related_context):
        conversation = [{"role": "system",

                 "content": "You are an expert at revamping resumes.\
                             You are designed to output JSON.\
                            You will be provided with a resume, which is used to describe the writer's experience and skills in his or her own word."},
                {"role": "user",
                  "content": f"Please filter out the first two professional or work or internship experiences out of the input resume\
                    only find out the company name and working content\
                    Take the content in brackets [ ] as input: [{related_context}]"
                },
                {"role": "user",
                 "content": "You have 6 tasks. \
                            1. The first one is that you need to check whether this resume is used to apply for jobs that relate\
                              to data scientist, data analyst, business analyst, and machine learning engineer. For this task, return 1 or 0, where 1 is yes and 0 is no, and the reason of it.\
                            2. the second is that you need to check the comprehensive technical coverage demonstrated in the resume.\
                              There are 11 technical skills required in the resume of data scientist, data analyst, business analyst, and machine learning engineer.\
                              return a number ranging from 1-5 and which skills are covered, where 5 means at least cover 5 skills, 4 means at least cover 4, 3 means at least cover 3,\
                              2 means at least cover 2, otherwise return 1. \
                            3. the third is that you need to check the grammer of the resume. Ignore the punctuation errors. Note that some grammer mistake can be accepted, for example\
                              the definite article can be omitted. return a number ranging from 1-5 and the grammer mistakes, where 5 means no or at most 2 grammer mistakes,\
                              4 means at most 4 mistakes, 3 means at most 6 mistakes, otherwise return 2. \
                            4. the forth is that you need to check the format standardization. Each bullet point in the resume should cover three parts: \
                              business or technical impact, for example, achieved 99% accuracy, reduced 10% cost, designed a system; the tech that you used, \
                              for example, linear regression, natural language processing model, a/b testing; the thing you did that can leverage the tech you mentioned to achieve the impact \
                              you illustrated before, for example, train a linear regression model to predict sales amount to increase 10% inventory turnover rate.\
                              return a range from 1-5 and the reason of it, where 5 means each bullet point contains all three parts; 4 means 80% bullet points contains all three parts;\
                              3 means 50% bullet points contains all three parts, and the other 50% contains 2 out of 3 parts; 2 means 30% bullet points contains three parts, and at most 30% \
                              of the bullet points contains only 1 part; otherwise, return 1;\
                            5. the last is that you need to check whether the resume illustrate the business sense. It can be shown by the business impact or writing research reports.\ business impact means \
                            the achievement in business, such as revenue, inventory turn over rate, etc. return 5 if at least 2 items show the busienss impact; return 3 if at least 1 shows\
                            the business impact; otherwise return 0;\
                            "
                },
                {"role": "user",
                 "content":"Below is the technical ability that should be illustrated in the resume of data scientist, data analyst, business analyst, and machine learning engineer: \
                              1. Building machine learning and deep learning models, including but not limited to linear regression,logistic regression,\
                                  XGBoost, random forest, neural networks; \
                              2. Training computer vision, natural language processing or large language model related model\
                              3. preprocessing the data, including but not limited to data cleaning, dealing with missing value and outliers;\
                              4. using skills to improve model performance, including but not limited to k-fold cross validation, feature selection,\
                                PCA, fine tuning;\
                              5. training time series model, including but not limited to moving average (MA), AR; \
                              6. Using database to store data, or extracting data from database\
                              7. Conducting industry or company research, including but not limited to performing SWOT analysis and analyzing annual report\
                              8. Using tools to do data visualization or building data dashboards, tools can be Power BI, Tableau, Python and R;\
                              9. Implementing A/B test"}]
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=conversation,
            temperature=0,
        )
        result = response.choices[0].message.content
        res = json.loads(result)
        return res

    def score(self, file_path):

        raw_text = self.read_text(file_path = file_path)
        print("======Successfully load file ==================")

        start, end = self.get_experience_position(raw_text)
        experience_related_content = raw_text[start:end]
        print("======Successfully extract experience related content from file ==================")

        res_json = self.openai_call(experience_related_content)
        print("======Successfully receive api call response from OpenAI ==================")

        return res_json 


# if __name__ == "__main__":

#     model = score_model()
#     ret = model.score(file_path = "./test_pdf/hang_guo_review_by_raymond.pdf")

#     print(ret)



        




