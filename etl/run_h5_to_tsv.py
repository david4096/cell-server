import os
for k in range(0, 31):
     os.system("python " + os.path.dirname(os.path.realpath(__file__)) + "/maketsv.py {}&".format(k))
