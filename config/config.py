import configparser


class Config:
    def __init__(self):
        super(Config, self).__init__()
        # self.path = r'D:\AAtestplaceforcode\CodeAudit\config\config.ini'
        self.path=r'C:\Users\chickey\Documents\huaxin\CodeAudit\config\config.ini'

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        return config


# if __name__ == '__main__':
#     con = Config()
#     ini = con.read_config()
#     print(ini['main_project']['project_path'])
