import re
import os
import sys
import pandas as pd
from collections import defaultdict

PREP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PREP_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")


class PatientSelector:
    def __init__(self, config: dict):
        self.config = config

    def process(self):
        data_path = os.path.join(DATA_DIR, self.config["PATIENTS_TABLE"]["FILE"])
        data = pd.read_excel(data_path)

        data.columns = self.config["PATIENTS_TABLE"]["COLS"]
        data["op_data"] = pd.to_datetime(data["op_date"].apply(lambda x: str(x)[:10]))

        data = data[self.config["PATIENTS_TABLE"]["SAVE_COLS"]]
        data.to_csv(os.path.join(OUTPUT_DIR, "patient.csv"), index=False)

        # Sex, Gender, ID
        sex_gender = os.path.join(DATA_DIR, self.c)


class RegexFeatureExtractor:
    def __init__(self, config: dict, keyword: dict):
        self.config = config
        self.keywords = keyword

    def add_operation_count(
        self, dataframe: pd.DataFrame, columns: str = "research_id"
    ) -> list:
        """수술기록지의 research_id을 기준으로 몇 번째의 수술인지 인덱싱해주는 함수

        Args:
            dataframe (pd.DataFrame)
            columns (str): 기준 컬럼

        Return:
            list: 각 row가 몇 번째 수술에 해당하는지 구하는 리스트
        """

        th_operations = [1]
        for i in range(1, len(dataframe)):
            if dataframe[columns][i] == dataframe[columns][i - 1]:
                th_operations.append(th_operations[-1] + 1)
            else:
                th_operations.append(1)

        return th_operations

    def determine_label(self, text: str) -> str:
        """Tag with malignant or negative

        Example
        ----------
        report_labeling(path_report['결과본문'][0])

        """

        malignant_regex = "|".join(self.keywords["LABEL"]["NEGATIVE"])
        negative_regex = "|".join(self.keywords["LABEL"]["POSITIVE"])

        if bool(re.search(malignant_regex, text)):
            return "Positive"
        elif bool(re.search(negative_regex, text)):
            return "Negative"
        else:
            return "Unknown"  # Neither postive or not

    def ext_non_muscular_inv(self, text: str) -> str:
        keyset = self.keywords["NM_INVASION"]
        positive_regex = "|".join(keyset["POSITIVE"])
        negative_regex = "|".join(keyset["NEGATIVE"])
        no_muscle_regex = "|".join(keyset["NO_MUSCLE"])

        # muscle invasion
        if bool(re.search(positive_regex, text)):
            return "Positive"
        elif bool(re.search(negative_regex, text)):
            return "Negative"
        elif bool(re.search(no_muscle_regex, text)):
            return "Unknown"
        return "Unknown"

    def ext_is_calcinoma(self, text: str, hist="UrothelialCarcinoma") -> bool:
        if hist == "UrothelialCarcinoma":
            TCC_regex = "|".join(self.keywords["UROTHELIAL_CA"])
            if bool(re.search(TCC_regex, text)):
                return True
            else:
                return False

    def truncate_report(self, txt: str) -> str:
        """Get the part of diagnosis

        Note:
            Component:
                Specimen: specimen list
            1) DIAGNOSIS:
            2) Results  of  immunohistochemical  studies (Optional)
            3) GROSS:


        """
        txt = txt.replace("\r", "")

        # 1st step: trim after 'DIAGNOSIS:'
        dx_reobj = re.search(r"diagnosis:", txt)

        if not dx_reobj:
            return
        txt = txt[dx_reobj.end() :].strip("\n")

        # 2nd step: delete after 'GROSS:' or 'Results  of  immunohistochemical  studies'
        gross_reobj = re.search("GROSS:", txt)
        histochem_start = re.search("Results  of  immunohistochemical", txt)

        if not gross_reobj:
            if not histochem_start:
                return txt
            return txt[: histochem_start.start()]

        else:
            if not histochem_start:
                return txt[: gross_reobj.start()]
            return txt[: min(gross_reobj.start(), histochem_start.start())]

    def split_specimen_info(self, txt):

        specimen_info = defaultdict(str)
        for idx, line in enumerate(txt.split("\n")):
            line = line.strip()

            # find start keyword e.g) a), b), c&d)
            name_reobj = re.search("[a-z](\&[a-z])*\)\s+", line)
            if name_reobj:
                specimen_name = line[name_reobj.end() :].strip()

                if ":" not in specimen_name:
                    idx += 1
                    line = line[idx].rstrip("\t")
                    if r":" in line:
                        specimen_name += line[: line.index(":")]
                else:
                    specimen_name = specimen_name.rstrip(":")

                idx += 1
                while idx < len(txt.split("\n")):
                    info_str = txt.split("\n")[idx].strip()

                    specimen_info[specimen_name] += info_str
                    idx += 1

        return specimen_info.keys()

    # def determine_
    # def __reg_bool(self, exp):
    #     import re

    #     return bool(re.search(exp, self.text))

    # def is_high_finder(self):
    #     """HIGH GRADE / LOW GRADE  찾기"""
    #     if self.__reg_bool("high"):  # HIGH GRADE 우선 검색
    #         return True
    #     elif self.__reg_bool("low(\s)+grade"):
    #         return False
    #     else:
    #         return "Unknown"

    # def get_highest_grade(self):
    #     """WHO GRADE 찾기"""
    #     import re

    #     pattern = "(who){0,1}(\s){0,2}(grade|GRADE)(\s){0,2}[1-3](\/)3"

    #     grade_list = []
    #     for item in re.finditer(pattern, self.text):
    #         tmp = item.group(0)
    #         grade = int(tmp.split()[-1].split("/")[0])
    #         grade_list.append(grade)
    #     try:
    #         return max(grade_list)
    #     except:
    #         return "Unknown"

    # def proper_muslce_finder(self):
    #     """Proper muslce 찾기"""

    #     ##FIND Proper muscle layer####
    #     proper_muslce_negative = [
    #         "presence.{0,2}(of){0,1}.{0,2}proper.{0,2}muscle.{0,2}layer",
    #         "presence.{0,2}(of){0,1}.{0,2}proper.{0,2}muslce.{0,2}without.{0,2}tumor",
    #         "proper.{0,2}muscle.{0,2}layer.{0,2}without.{0,2}tumor.{0,2}involvement",
    #         "proper.{0,2}muscle(\s){0,2}layer{0,1}(\s){0,2}(present){0,1}(\s){0,2}with.{0,2}no.{0,2}tumor",
    #         "\)(?!.*no)(\s){0,2}proper.{0,2}muscle.{0,2}present(\\.){0,1}",
    #         "proper  muscle,  no  tumor  present",
    #         "no stromal  and  proper  muscle  invasion",
    #         "no proper(\s){0,3}muscle(\s){0,3}invasio",
    #     ]
    #     absent_proper_muscle = [
    #         "proper.{0,2}muscle.{0,2}absent",
    #         "no.{0,3}proper.{0,3}muscle.{0,3}present",
    #         "absence.{0,2}of.{0,2}proper.{0,2}muscle",
    #         "no.{0,2}muscularis.{0,2}propria.{0,2}present",
    #         "absence   of  proper  muscle  layer",
    #         "Absence  of  muscularis  propria",
    #     ]
    #     muscle_invasion = [
    #         "\)(?!.*no)(\s){0,2}proper.{0,2}muscle.{0,2}invasion",
    #         "\)(?!.*no)(\s){0,2}invasion(\s){0,2}into(\s){0,3}subepithelial(\s){0,3}connective(\s){0,3}tissue(\s)*and(\s){0,3}muscular",
    #         "\)(?!.*no)(\s){0,2}invasion.{0,2}into.{0,2}musc.{0,4}",
    #         "with  proper  muscle  involvement",
    #     ]

    #     if self.__reg_bool("|".join(muscle_invasion)):
    #         return "Invasion into muscle"
    #     elif self.__reg_bool("|".join(proper_muslce_negative)):
    #         return "Muscle intact"
    #     elif self.__reg_bool("|".join(absent_proper_muscle)):
    #         return "Unknown"
    #     else:
    #         return "Unknown"

    # def lymovascular_invasion(self):
    #     """Lymphovascular invasion"""
    #     lymphovas_reg = ["lymphovascular(\s){0,2}invasion(\s):(\s){0,2}identified"]
    #     no = [
    #         "no(\s){0,2}lymphovascular(\s){0,2}invasion",
    #         "\)(?!.*no)(\s){0,2}lymphovascular  invasion:  not  identified",
    #         "t1b",
    #     ]
    #     if self.__reg_bool("|".join(lymphovas_reg)):
    #         return True
    #     elif self.__reg_bool("|".join(no)):
    #         return False
    #     else:
    #         return "Unknown"

    # def stromal_invasion(self):
    #     no_stromal_inv_reg = [
    #         "no(\s){0,3}stromal(\s){0,3}invasion",
    #         "no  invasion  into  subepithelial  connective  tissue",
    #     ]
    #     stromal_inv_regex = [
    #         "stromal  invasion",
    #         "invasion  into  subepithelial  connective  tissue",
    #     ]
    #     if self.proper_muslce_finder() == "Invasion into muscle":
    #         return True
    #     elif self.__reg_bool("|".join(no_stromal_inv_reg)):
    #         return False
    #     elif self.__reg_bool("|".join(stromal_inv_regex)):
    #         return True
    #     else:
    #         return "Unknown"

    # def stage_finder(self):
    #     # Class T stage
    #     # * Ta : Papillary epitherlium
    #     # * T1: Lamina propia invasion
    #     # * T2: Muscle invasion

    #     t1_exp = [
    #         "invasion  into  subepithelial  connective  tissue",
    #         "t1a",
    #         "at  least  t1a",
    #     ]
    #     lamina_invasion = [
    #         "lamina  propria  invasion",
    #         "suburethral  connective  tissue  invasion",
    #     ]
    #     # no stromal invasion -> Ta
    #     # CIS ->
    #     if self.proper_muslce_finder() == "Invasion into muscle":
    #         return "T2"
    #     elif (
    #         (self.proper_muslce_finder() == "Muscle intact")
    #         & (self.stromal_invasion() == True)
    #         | self.__reg_bool("|".join(lamina_invasion))
    #         | self.__reg_bool("|".join(t1_exp))
    #     ):
    #         return "T1"
    #     elif self.stromal_invasion() == False:
    #         return "Ta"
    #     else:
    #         return "CIS"

    # def pprint(self):
    #     import re

    #     print(re.sub("\r", "\n", self.text))

    # def feature_export(self):
    #     import pandas as pd

    #     row = [
    #         self.is_high_finder(),
    #         self.get_highest_grade(),
    #         self.proper_muslce_finder(),
    #         self.stage_finder(),
    #         self.lymovascular_invasion(),
    #         self.stromal_invasion(),
    #     ]
    #     row = pd.DataFrame(
    #         [row],
    #         columns=[
    #             "High_grade",
    #             "Max_WHO_grade",
    #             "Muscle",
    #             "Stage",
    #             "LV_invasion",
    #             "stromal_invasion",
    #         ],
    #     )
    #     return row

    def preprocess(self):

        # Read data
        reports = pd.read_csv(self.config["PATHOLOGY_REPORTS"]["FILE"])
        reports = reports[self.config["PATHOLOGY_REPORTS"]["COLS"]]
        reports["result"] = reports["result"].apply(lambda x: x.lower())

        # Re-index
        count_num = pd.DataFrame(reports.research_id.value_counts())
        count_num.reset_index(inplace=True)
        count_num.rename(
            columns={"research_id": "total_operation", "index": "research_id"},
            inplace=True,
        )
        reports = pd.merge(reports, count_num, on="research_id")

        # Add features
        reports["th_operation"] = self.add_operation_count(reports)
        reports["label"] = reports["result"].apply(lambda x: self.determine_label(x))
        reports["muscle_inv"] = reports["result"].apply(
            lambda x: self.ext_non_muscular_inv(x)
        )
        reports["is_urothelial_ca"] = reports.result.apply(
            lambda x: self.ext_is_calcinoma(x)
        )
        reports["diagnosis"] = reports["result"].apply(
            lambda x: self.truncate_report(x)
        )

        reports.to_csv(
            os.path.join(OUTPUT_DIR, "pathologic_reports_feature.csv"), index=False
        )
        print(reports)
