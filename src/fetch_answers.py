# %%
import taskanalytics_data_wrapper.taskanalytics_api as task
from dotenv import load_dotenv
import os
# %%
load_dotenv()
# %%
email = os.getenv("ta_email")
password = os.getenv("ta_password")
survey_id = os.getenv("ta_survey_id")
# %%
get_survey = task.download_survey(
    username=email, password=password, survey_id=survey_id, filename_path="../data/new/survey.csv"
)
get_survey.status_code
# %%
