# Coding: utf-8
# Last Version update 2019.11.24
# Developed by HH

import re

# 병리기록지 암/음성 반환
# 병리기록지 암/음성 반환


# 병리조직 반환
def histological_type(text, hist="UrothelialCarcinoma"):
    """Classify the pathologic report related to histological type
    Parameters
    ----------
    text: Str.
    hist: Str.
        defualt:'UrothelialCarcinoma'
    Return
    ----------
    Boolean

    """

    import re

    if hist == "UrothelialCarcinoma":
        TCC_dict = [
            "UROTHELIAL.{0,4}CARCINOMA",
            "INFILTRATING  TRANSITIONAL  CELL  CARCINOMA",
            "urothelial.{0,3}carcinoma.{0,3}in.{0,3}situ",
            "transitional.{0,2}carcinoma",
            "T.{0,2}C.{0,2}C",
            "Papillary.{0,3}urothelial.{0,3}carcninoma",
        ]
        TCC_regex = "|".join(TCC_dict)  # Making regex expression
        if bool(re.search(TCC_regex, text)):
            return True
        else:
            return False


# 불용어 삭제
def stopwords_removal(tokens):
    """Stop words processing
    Parameters
    ----------
    token: list. list must inlcude comma splitted string (token)

    Returns
    ----------
    list.


    Example:
    word_tokens = word_tokenize(path_report['결과본문'][0])
    stopwords_removal(word_tokens)
    """
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    stop_words = set(stopwords.words("english"))
    filtered_sentence = []

    # After Parsing and removing stopwords, merging token
    for w in tokens:
        if w not in stop_words:
            filtered_sentence.append(w)

    return filtered_sentence


# Trimming
def trimming(text):
    import re

    text = text.replace("\r", "")

    # 1st step: trim after 'DIAGNOSIS:'
    diagnosis_key = ["DIAGNOSIS:", "Diagnosis:"]
    start_idx = re.search("|".join(diagnosis_key), text).end()
    first_trim_text = text[start_idx:]

    # 2nd step: delete after 'GROSS:' or 'Results  of  immunohistochemical  studies'
    gross_key = re.search("GROSS:", first_trim_text)
    RIS_key = re.search("Results  of  immunohistochemical", first_trim_text)

    if gross_key == None:
        if RIS_key == None:
            return first_trim_text
        else:
            return first_trim_text[: RIS_key.start()]

    else:
        if RIS_key == None:
            return first_trim_text[: gross_key.start()]
        else:
            return first_trim_text[: min(gross_key.start(), RIS_key.start())]


# Split diagnosis
def find_diagnosis(text):
    find_obj = "[A-Z]\)|[A-Z]&[A-Z]\)|[A-Z]-[A-Z]\)|[A-Z],[A-Z]\)"

    compile_obj = re.compile(find_obj)
    obj_list = compile_obj.split(text)
    if len(obj_list) == 1:
        return obj_list
    else:
        return obj_list[1:]


def add_lead_feature(dataframe, index_column, target_column):
    """
    This function is for making lead feature of 'target column' by 'index_column'.
    It means that if you have repetitive index, it brings next value for every rows.
    So the last repetitive index, it makes 'last' value to show that row is the last row of same indexes.

    If you don't have any repetitive index, I recommend you to use 'shift' function in 'pandas' package.
    """
    lead_label = []

    for i in range(0, len(dataframe) - 1):
        if dataframe[index_column][i] == dataframe[index_column][i + 1]:
            lead_label.append(dataframe[target_column][i + 1])
        else:
            lead_label.append("last")
    lead_label.append("last")
    dataframe["lead_label"] = lead_label

    return dataframe


def get_final_value(dataframe, index_column, target_column):

    """
    This function works to get final value of 'target column' in same 'index_column'.
    It means that if you have repetitive index, it brings final value for first index row.
    So only the first row of same index get the value of the last one, and the others get 'drop'.
    Also, this function return 'only_one' to the number of certain index is one.

    If the first row of dataframe is not the 'only_one', it will make error. Please amend the code to fit your case.
    Plus, if you don't have any repetitive index, I recommend you to use 'shift' function in 'pandas' package.
    """

    index_col = list(dataframe[index_column])
    final_value = []

    for i in range(0, len(dataframe) - 1):
        if index_col.count(dataframe[index_column][i]) == 1:
            final_value.append("only_one")
        else:
            if dataframe[index_column][i - 1] != dataframe[index_column][i]:
                final_index = i + index_col.count(dataframe[index_column][i]) - 1
                final_value.append(dataframe[target_column][final_index])
            else:
                final_value.append("drop")
    final_value.append("drop")
    dataframe["final_value"] = final_value

    return dataframe


# 특수문자 제거 함수
def cleanText(texts):
    import re

    text = re.sub("[-+,!@#$%^&*\\\"'\(\)\[\]\<\>\-\_=\|/:]", "", texts)
    return text


# 필요없는 부분인 'urinary bladder transurethral resection' 부분 삭제
def del_transurethral_resection(text):
    import re

    resection_key = re.search("transurethral resection", text)
    if resection_key == None:
        return text
    else:
        del_index = resection_key.end()
        return text[del_index + 1 :]


# Trimming_gross
def trimming_gross(text):
    import re

    text = text.replace("\r", "")

    # 1st step: trim after 'GROSS:'
    gross_key = ["GROSS:", "gross:"]
    start_idx = re.search("|".join(gross_key), text).end()
    first_trim_text = text[start_idx:]

    # 2nd step: delete after 'DIAGNOSIS:' or 'Results  of  immunohistochemical  studies'
    diagnosis_key = re.search("DIAGNOSIS:", first_trim_text)
    RIS_key = re.search("Results  of  immunohistochemical", first_trim_text)

    if diagnosis_key == None:
        if RIS_key == None:
            return first_trim_text
        else:
            return first_trim_text[: RIS_key.start()]

    else:
        if RIS_key == None:
            return first_trim_text[: diagnosis_key.start()]
        else:
            return first_trim_text[: min(diagnosis_key.start(), RIS_key.start())]


# gross에서 tissue size 계산하는 함수
def gross_tissue_size(text):
    import re
    from nltk.tokenize import word_tokenize

    # If there's 'cm' in text, get max lenght of tissue.
    if [i.start() for i in re.finditer("cm", text)] != []:
        cm_idx = [i.start() for i in re.finditer("cm", text)]
        total_text = ""
        for i in cm_idx:
            target_text = text[i - 16 : i]
            total_text += " " + target_text
        total_text = re.sub("[a-z/]", "", total_text)
        total_text = re.sub("[ㄱ-ㅣ가-힣]", "", total_text)

        # If there's '.' in list, it arises "ValueError: could not convert string to float: '.'"
        length_list = [
            float(i) if i != "." else 0
            for i in word_tokenize(re.sub("[a-z]", " ", total_text))
        ]
        return max([value for value in length_list if value != "."])

    # If there's no 'cm' in text, find 'cc' and get cube root of cc num.
    else:
        if [i.start() for i in re.finditer("cc", text)] != []:
            cc_idx = [i.start() for i in re.finditer("cc", text)]
            total_text = ""
            for i in cc_idx:
                target_text = text[i - 5 : i]
                total_text += " " + target_text
            total_text = re.sub("[a-z/]", "", total_text)
            length_list = [
                float(i) if i != "." else 0
                for i in word_tokenize(re.sub("[a-z]", " ", total_text))
            ]

            # this value is 'cc', so it has to be cube rooted value
            return pow(max([value for value in length_list if value != "."]), 1 / 3)

        else:
            return None


# 특정 인덱스 키를 기준으로 앞에서 나온 row 인지 count 하는 함수
def row_index_count(dataframe, index_col):
    temp_list = [1]
    for i in range(1, len(dataframe)):
        if dataframe[index_col][i] == dataframe[index_col][i - 1]:
            temp_list.append(temp_list[-1] + 1)
        else:
            temp_list.append(1)
    return temp_list
