from time import time, localtime, strftime
from google.cloud import secretmanager
import numpy as np

import os
def hente_hemmeligheter(hvilke: "String") -> None:
    """
    Definerer posisjon til hemmeligheter og henter ut hemmeligheter.
    Hemmelighetene lagres i environment.
    
    :param: hvilke: angir hvilke hemmeligheter du skal hente ut.
    """
    os.environ.update({"KNADA_MY_SECRET": "projects/193123067890/secrets/anders-lauvland/versions/latest"})
    resource_name = os.environ["KNADA_MY_SECRET"]
    from google.cloud import secretmanager
    start = time()
    print("Lager en 'secret' instans...")
    
    secrets = secretmanager.SecretManagerServiceClient()
    resource_name = os.environ["KNADA_MY_SECRET"]
    
    print("...henter hemmeligheter...")
    secret = secrets.access_secret_version(name=resource_name)
    hemmeligheter = eval(secret.payload.data.decode('UTF-8'))[hvilke] # evalueres direkte til en dict.
    del secrets
    os.environ.update(hemmeligheter)
    print("...sånn...")
    end = time()
    now = strftime("%d/%m/%Y %H:%M:%S", localtime())
    print(f"...ferdig {now}, og det tok {np.round(end-start, 2)} sekunder.")
    if hvilke == "TaskAnalytics":
      os.environ.update({"survey_id": "03401"})






