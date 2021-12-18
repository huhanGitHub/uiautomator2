import os
import json
intent_smali_fileds = 'Landroid/content/Intent;->get'
const_string = 'const-string'

def intent_field_extractor(path):
    log = r'intent_smali_analysis.txt'
    fields = {}
    with open(log, 'a+', encoding='utf8') as log:
        for root, dirs, files in os.walk(path):
            for file in files:
                if str(file).endswith('smali'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r+', encoding='utf8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if intent_smali_fileds in line:
                                index = line.index(intent_smali_fileds)
                                end = line.index('(', index)
                                field = line[index:end]
                                field = field.replace(';\n', '')
                                field = field.replace('Landroid/content/Intent;->', '')
                                counts = fields.setdefault(field, 0)
                                counts += 1
                                fields[field] = counts

        fields = sorted(fields.items(), key=lambda d: d[1], reverse=True)
        for k, v in fields:
            log.write(k + ' ' + str(v) + '\n')


def smali_intent_para_extractor():
    path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/smali_samples/smalis'
    save_path = r'intent_para.json'
    apps_intent_para = {}
    apps = [i for i in os.listdir(path)]
    for app in apps:
        app_path = os.path.join(path, app)
        intent_para = {}
        for root, dirs, files in os.walk(app_path):
            for file in files:
                if 'activity' in file or 'Activity' in file:
                    if file.endswith('.smali') and '$' not in file:
                        file_path = os.path.join(root, file)
                        pairs = []
                        with open(file_path, 'r+', encoding='utf8') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if intent_smali_fileds in line:
                                    index = line.index(intent_smali_fileds)
                                    end = line.index('(', index)
                                    field = line[index:end]
                                    field = field.replace(';\n', '')
                                    field = field.replace('Landroid/content/Intent;->', '')

                                    # find const string in the previous lines
                                    pre_index = i - 1
                                    while pre_index >= 0:
                                        temp = lines[pre_index]
                                        if const_string in lines[pre_index]:
                                            tag = lines[pre_index].strip()
                                            tag = tag[tag.index('"') + 1: tag.rindex('"')]
                                            tag = tag.replace('\n', '')
                                            pair = [tag, field]
                                            pairs.append(pair)
                                            print(temp)
                                            break
                                        else:
                                            pre_index = pre_index - 1

                            if len(pairs) != 0:
                                intent_para[file] = pairs

        apps_intent_para[app] = intent_para
    save_json = json.dumps(apps_intent_para)
    with open(save_path, 'a+', encoding='utf8') as f2:
        f2.write(save_json)


if __name__ == '__main__':
    path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/recompile samples'
    # intent_field_extractor(path)
    smali_intent_para_extractor()