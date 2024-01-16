import json

source_path = "api_clinical_trials_response.json"

with open(source_path, "r", encoding="utf-8") as f:
    clinical_trials_json = json.load(f)

study_list = clinical_trials_json['FullStudiesResponse']['FullStudies']

out_csv = ""
out_firstline = "ID|Type|Intervention Type|Phases|Allocation|Masking|Title|Status|Start|Update|Summary|Conditions|Keywords|Eligibility|Arms\n"

for study in study_list:
    study_item = study['Study']
    section = study_item['ProtocolSection']['IdentificationModule']
    study_id = section['NCTId']
    if 'OfficialTitle' in section:
        title = section['OfficialTitle']
    else:
        title = section['BriefTitle']

    section = study_item['ProtocolSection']['StatusModule']
    status = section['OverallStatus']
    submitted = section['StudyFirstPostDateStruct']['StudyFirstPostDate']
    updated = section['LastUpdatePostDateStruct']['LastUpdatePostDate']

    section = study_item['ProtocolSection']['DescriptionModule']
    brief_summary = section['BriefSummary']

    eligibility = study_item['ProtocolSection']['EligibilityModule']['EligibilityCriteria']

    section = study_item['ProtocolSection']['ConditionsModule']
    conditions = ",".join(section['ConditionList']['Condition'])
    if 'KeywordList' in section:
        keywords = ",".join(section['KeywordList']['Keyword'])
    else:
        keywords = ""

    section = study_item['ProtocolSection']['DesignModule']
    study_type = section['StudyType']
    if 'DesignInterventionModel' in section['DesignInfo']:
        intervention_type = section['DesignInfo']['DesignInterventionModel']
    else:
        intervention_type = ""
    if 'PhaseList' in section:
        phases = ",".join(section['PhaseList']['Phase'])
    else:
        phases = ""
    if 'DesignAllocation' in section['DesignInfo']:
        allocation = section['DesignInfo']['DesignAllocation']
    else:
        allocation = ""
    if 'DesignMaskingInfo' in section['DesignInfo']:
        masking = section['DesignInfo']['DesignMaskingInfo']['DesignMasking']
    else:
        masking = ""

    extra_columns = []
    if 'ArmGroupList' in study_item['ProtocolSection']['ArmsInterventionsModule']:
        arm_list = study_item['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']
        for arm in arm_list:
            if 'ArmGroupInterventionList' in arm:
                interventions = ",".join(arm['ArmGroupInterventionList']['ArmGroupInterventionName'])
                extra_columns.append(interventions)
            else:
                if 'ArmGroupType' in arm:
                    interventions = arm['ArmGroupType']
                else:
                    interventions = arm['ArmGroupLabel']
    else:
        interventions = [x['InterventionName'] for x in study_item['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention']]
        extra_columns.append(",".join(interventions))

    new_line = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (study_id, study_type, intervention_type, phases, allocation, masking, title, status, submitted, updated, brief_summary, conditions, keywords, eligibility)
    for extra_column in extra_columns:
        new_line += "|"+extra_column

    new_line = new_line.replace("\n", " ")
    new_line += "\n"
    out_csv += new_line

out_csv = out_firstline+out_csv

with open("clinicaltrials.csv", "w", encoding="utf-8") as f:
    f.write(out_csv)