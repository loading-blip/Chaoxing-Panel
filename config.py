import yaml

class Config:
    def __init__(self) -> None:
        yaml_file = yaml.load(open("config.yaml",'r',encoding='utf8'),Loader=yaml.FullLoader)
        self.use_cookies = yaml_file['Account']['use_cookies']
        self.user_name = yaml_file['Account']['username']
        self.password = yaml_file['Account']['password']
        self.cookies_file_path = yaml_file['Account']['cookies_file_path']
        self.btn_reg_names = yaml_file['Mapping_table']['button_name'][0]
        self.btn_can_reg_names = yaml_file['Mapping_table']['button_name'][1]
        self.btn_cannot_reg_names = yaml_file['Mapping_table']['button_name'][2]
        self.btn_reg_full_names = yaml_file['Mapping_table']['button_name'][3]
        self.btn_over_dl_names = yaml_file['Mapping_table']['button_name'][4]
