def main():
    import time
    import pandas as pd
    from datetime import date, datetime, timedelta
    import os
    import re
    import numpy as np
    import logging
    import sys
    from pathlib import Path
    sys.path.append(r"J:\Admin & Plans Unit\Recovery Systems\1. Systems\Python Scripts\Morning Script\modules")

    if __name__ == "__main__":
        import Shira
        from Shira import Webex_Alarm, webex_bot, Newest_file,refresh_excel, Replace_File, df_to_csv_replace
    else:
        from modules import Shira
        from modules.Shira import Webex_Alarm, webex_bot, Newest_file, refresh_excel,Replace_File, df_to_csv_replace

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    
    file_handler = logging.FileHandler('appeal.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # PRS_ASSIGNED = r"J:\Admin & Plans Unit\Recovery Systems\4. Team Folder\Jonathan\Jonathan Projects\PR Assignment\data"
    DESTINATION_FOLDER = r'J:\Admin & Plans Unit\Recovery Systems\1. Systems\Python Scripts\Morning Script\modules\Assign_Programmatic_Reviewer\data'
    FLPA_ACCOUNTS = r"J:\Admin & Plans Unit\Recovery Systems\2. Reports\4. Data Files\FLPA Accounts Export"
    ALL_EVENTS = r"J:\Admin & Plans Unit\Recovery Systems\2. Reports\4. Data Files\FLPA Grants"
    PR_LIST = ['John Hayth', 'Hamza Sattar', 'Ashley Mitchell', 'Collin Kenline', 'Rachel Langston', 'Haley Beary', 'Travis Ancion']
    CLASSIFICATION_REGEX_DICT = {'Collin Kenline': ['State Agency'], 'Hamza Sattar': ['Water Management District'], 'Rachel Langston': ['County Sheriff']}
    KEYWORD_REGEX_DICT = {'John Hayth': ['Electric Coop', 'ELECTRIC COOP', 'Elec Co-', 'ELEC CO-', 'Electric Membership', 'ELECTRIC MEMBERSHIP', 'Utility Authority',  'UTILITY AUTHORITY', 'Utilities Authority', 'UTILITIES AUTHORITY', 'Electric Authority', 'ELECTRIC AUTHORITY'], 'Rachel Langston': ['fire', 'FIRE']}
    file_name = f'PR_Assignments_{date.today().strftime("%Y-%#m-%#d")}'


    class PR:
        def __init__(self, name: str, events: list):
            self.name = name
            self.events = events
            self.events_dict = {}
            for key in events:
                self.events_dict[key] = 0
            self._keyword_regex_pattern = None
            self._classification_regex_pattern = None

        def get_score(self, event:str) -> float:
            event_score = self.events_dict[event]
            account_score = self.events_dict['Account_Total_Count']/100000
            score = event_score + account_score

            return score

        @property
        def keyword_regex_pattern(self):
            if self._keyword_regex_pattern is None:
                return None
            
            return self._keyword_regex_pattern

        @keyword_regex_pattern.setter
        def keyword_regex_pattern(self, patterns: list[str]):
            self._keyword_regex_pattern = patterns

        @property
        def classification_regex_pattern(self):
            if self._classification_regex_pattern is None:
                return None
            
            return self._classification_regex_pattern

        @classification_regex_pattern.setter
        def classification_regex_pattern(self, patterns: list[str]):
            self._classification_regex_pattern = patterns

        def __update_account_total_after_increment(func):
            def inner(self, event):
                func(self, event)
                account_count = 0
                for key, value in self.events_dict.items():
                    if key != 'Account_Total_Count':
                        account_count += value
                # account_count = sum(self.events_dict.values())
                self.events_dict['Account_Total_Count'] = account_count
                
            return inner
        
        def __update_account_total(func):
            def inner(self, event, **kwargs):
                self.count = kwargs['count']
                func(self, event, **kwargs)
                account_count = 0
                for key, value in self.events_dict.items():
                    if key != 'Account_Total_Count':
                        account_count += value
                # account_count = sum(self.events_dict.values())
                self.events_dict['Account_Total_Count'] = account_count

            return inner
        
        @__update_account_total_after_increment
        def increment_event(self, event:str):
            self.events_dict[event] += 1
            
        @__update_account_total
        def add_event(self, event: str, **kwargs):
            self.count = kwargs['count']
            if self.count == None and event in self.events:
                print(f'{event} already exist. Value not updated')
            elif self.count != None and event in self.events:
                self.events_dict[event] = self.count
                print(f'{event} value updated to {self.count}')
            else:
                self.events_dict[event] = self.count
                print(f'{event} added with a value of {self.count}')

        def get_events_dict(self):
            return self.events_dict
            
        def get_events_list(self):
            return self.events
        
        def get_total_event_count(self):
            return sum(self.events_dict.values())

        def get_name(self):
            return self.name


    def read_latest_csv_file(attachment_folder):
        fileNames=[]
        for file in os.listdir(attachment_folder):
            fileNames.append(file)
        sorted_file_names = sorted(fileNames, reverse=True)

        return pd.read_csv(attachment_folder+"/"+sorted_file_names[0], encoding='ISO-8859-1') 


    def create_df(from_folder):
        df = read_latest_csv_file(from_folder)

        return df
    

    def merge_dfs(one_df: pd.DataFrame, two_df: pd.DataFrame, on_columnns: list[str], how: str, filter: str) -> pd.DataFrame:
        merged_df = one_df.merge(two_df, on=on_columnns, how=how, indicator=True)
        filtered_df = merged_df[merged_df['_merge'] == filter]
        cleaned_df = filtered_df.drop('_merge', axis=1)

        return cleaned_df


    def get_prs_assigned_df(prs_assigned: str) -> pd.DataFrame:
        prs_assigned_df = create_df(prs_assigned)
        prs_assigned_df['Grant #'] = prs_assigned_df['Grant #'].astype(str)

        return prs_assigned_df
    

    def get_flpa_account_df(flpa_accounts: str) -> pd.DataFrame:
        flpa_accounts_df = create_df(flpa_accounts)
        flpa_accounts_df['Grant #'] = flpa_accounts_df['Grant #'].astype(str)
        flpa_accounts_df = flpa_accounts_df[~flpa_accounts_df['Grant #'].str.contains('-')]
        #Added for testing
        flpa_accounts_df = flpa_accounts_df[flpa_accounts_df['Account Status'] != 'Closed']

        return flpa_accounts_df


    def get_unique_accounts_to_be_assigned(prs_assigned_df: pd.DataFrame, flpa_accounts_df: pd.DataFrame) -> pd.DataFrame:
        # Get Applicants Not Assigned PRs
        columns_to_drop = ['PR', 'FIPS #', 'Account Status', 'County', 'Classification']
        prs_assigned_stripped_df = prs_assigned_df.drop(columns=columns_to_drop)
        unique_applicants = merge_dfs(flpa_accounts_df, prs_assigned_stripped_df, ['Applicant Name', 'Grant #'], 'left', 'left_only')
        unique_applicants.drop_duplicates(subset='Applicant Name', inplace=True)
        columns_to_keep = ['Grant #','Applicant Name', 'Account Status','FIPS #', 'County', 'Classification']
        unique_accounts_to_be_assigned = unique_applicants[columns_to_keep]

        return unique_accounts_to_be_assigned


    def update_event_total_by_pr_df(currently_assigned: pd.DataFrame, pr_obj_list: list[object], events: list[str]) -> list[object]:
        for i in pr_obj_list:
            for event in events:
                conditions_met_df = (currently_assigned['PR'] == i.name) & (currently_assigned['Grant #'] == event) & (currently_assigned['Account Status'] != 'Closed')
                count = conditions_met_df.sum()
                i.add_event(event, count=count)

        return pr_obj_list


    def get_open_events(flpa_events_path: str) -> list[str]:
        df6 = create_df(flpa_events_path)
        df6 = df6[df6['Closed Date'].isnull()]
        df6['Grant #'] = df6['Grant #'].astype(str)
        flpa_open_events = df6['Grant #'].tolist()

        return flpa_open_events


    def zip_to_dict(key: list, value: list[float] | list[list]) -> dict:
        new_dict = {key: value for key, value in zip(key, value)}
        
        return new_dict
    

    def initiate_pr_objects(pr_list: list[str], events: list[str]) -> dict:
        pr_object_list = []
        for pr in pr_list:
            obj = PR(pr, events)
            pr_object_list.append(obj)

        return pr_object_list
    

    def add_regex_patterns_to_pr(pr_class_list: list[object], pr_list: list[str], regex: dict, dict_name: str) -> None:
        [setattr(pr_class_list[idx], dict_name, regex[pr]) for idx, pr in enumerate(pr_list) if pr in regex]

        return
    

    def assign_pr_to_existing_applcants(existing_applicants_to_assign_accounts: pd.DataFrame, currently_assigned) -> pd.DataFrame:
        selected_columns = ['PR', 'Applicant Name']
        currently_assigned = currently_assigned[selected_columns]
        currently_assigned = currently_assigned.drop_duplicates(subset='Applicant Name')
        assignment_records = existing_applicants_to_assign_accounts.merge(currently_assigned, on=['Applicant Name'], how='left', indicator=True)
        assignment_records = assignment_records[assignment_records['_merge'] == 'both']
        assignment_records.drop('_merge', axis=1, inplace=True)

        return assignment_records


    def append_dfs(*args: pd.DataFrame | list[pd.DataFrame]) -> pd.DataFrame:
        if not args:
            raise ValueError("At least one DataFrame must be provided")
        elif len(args) == 1 and isinstance(args[0], list):
            dataframes = args[0]
            result = pd.concat(dataframes, ignore_index=True)
        else:
            dataframes = args
            result = pd.concat(dataframes, ignore_index=True)
        
        return result


    def assign_pr_to_new_applcants(non_existing_applicants_df: pd.DataFrame, pr_list: list[object], og_pr_list: list[str]) -> pd.DataFrame:
        # Get PR score based on event
        for index, row in non_existing_applicants_df.iterrows():
            score_list = []
            pr_name_list = []
            for pr in pr_list:
                applicant = row['Applicant Name']
                event = row['Grant #']
                score = pr.get_score(event)
                score_list.append(score)
                name = pr.get_name()
                pr_name_list.append(name)

            pr_score_dict = zip_to_dict(pr_name_list, score_list)

            # Select the PR with the lowest score and assign to applicant event record
            pr_to_assign = min(pr_score_dict, key = pr_score_dict.get)
            non_existing_applicants_df.loc[index, 'PR'] = pr_to_assign

            # Increase the newly assigned PR's score by one
            pr_list_index = og_pr_list.index(pr_to_assign)
            pr_list[pr_list_index].increment_event(event)
        
        updated_non_existing_applicants_df = non_existing_applicants_df

        return updated_non_existing_applicants_df


    def check_patterns(value, patterns: list[str]) -> bool:
        for pattern in patterns:
            if re.search(pattern, value):
                return True
            
        return False

   
    def assign_prs_with_regex_patterns(non_existing_applicants_df, column_to_check, pr_name_regex_tuple):
        for index, row in non_existing_applicants_df.iterrows():
            for name, regex_pattern in pr_name_regex_tuple:
                if check_patterns(row[column_to_check], regex_pattern):
                    non_existing_applicants_df.loc[index, 'PR'] = name
        
        print('This is the key word assigned records')
        print(non_existing_applicants_df)
        df_cleaned = non_existing_applicants_df[non_existing_applicants_df['PR'].notna()]

        return df_cleaned
        

    def get_pr_assignment(events: list[str], pr_list: list[str], classification_regex_dict: dict, keyword_regex_dict: dict, DESTINATION_FOLDER, FLPA_ACCOUNTS) -> None:
        # Get Dataframes
        currently_assigned = get_prs_assigned_df(DESTINATION_FOLDER)
        flpa_accounts_df = get_flpa_account_df(FLPA_ACCOUNTS)
        accounts_to_assign = get_unique_accounts_to_be_assigned(currently_assigned, flpa_accounts_df)
        print('Accounts to be assigned')
        print(accounts_to_assign)
        open_events = get_open_events(events)
        apps_already_assigned_list = currently_assigned['Applicant Name'].tolist()
        existing_applicants_df = accounts_to_assign[accounts_to_assign['Applicant Name'].isin(apps_already_assigned_list)]
        non_existing_applicants_df = accounts_to_assign[~accounts_to_assign['Applicant Name'].isin(apps_already_assigned_list)]
        non_existing_applicants_df['PR'] = np.nan


        # Create list[obj] of Programmatic Reviewers
        pr_class_list = initiate_pr_objects(pr_list, open_events)

        # Add regex patterns to Programmatic Reviewers
        add_regex_patterns_to_pr(pr_class_list, pr_list, keyword_regex_dict, 'keyword_regex_pattern')
        add_regex_patterns_to_pr(pr_class_list, pr_list, classification_regex_dict, 'classification_regex_pattern')
    
        # Assign accounts to Programmatic Reviewer who are already assigned those applicants accounts
        pr_assignments_existing_applicants = assign_pr_to_existing_applcants(existing_applicants_df, currently_assigned)
        appended_currently_assigned_df = append_dfs(currently_assigned, pr_assignments_existing_applicants)

        appended_currently_assigned_df.to_csv("J:\\Admin & Plans Unit\\Recovery Systems\\1. Systems\\Python Scripts\\Morning Script\\modules\\Assign_Programmatic_Reviewer\\test\\currently_assigned\\test.csv", index=False)


        # Update the Programmatic Reviewer objects with an open events dictionary and add a assignment count value to each event key
        updated_obj_list = update_event_total_by_pr_df(appended_currently_assigned_df, pr_class_list, open_events)

        # Assign new applicant accounts to Programmatic Reviewers
        if non_existing_applicants_df.shape[0] > 0:
            # Assign accounts that have classifications with default PRs
            pr_name_regex_tuple = [(obj.name, obj.classification_regex_pattern) for obj in pr_class_list if obj.classification_regex_pattern is not None]
            pr_assignments_with_classification_df = assign_prs_with_regex_patterns(non_existing_applicants_df, 'Classification', pr_name_regex_tuple)
            print('New assignments made by classification')
            print(pr_assignments_with_classification_df)
            pr_assignments_with_classification_df.to_csv("J:\\Admin & Plans Unit\\Recovery Systems\\1. Systems\\Python Scripts\\Morning Script\\modules\\Assign_Programmatic_Reviewer\\test\\assignments_classification\\test.csv", index=False)

            # Get remaining accounts (accounts with classifications that do not have default PRs)
            merge_columns = ['Grant #','Applicant Name', 'Account Status','FIPS #', 'County', 'Classification', 'PR']
            non_existing_applicants_no_default_catigory_df = merge_dfs(non_existing_applicants_df, pr_assignments_with_classification_df, merge_columns, 'left', 'left_only')
            print('These are new accounts with no default catigories')
            print(non_existing_applicants_no_default_catigory_df)

            # Assign PRs by keyword (from the above remaining accounts)
            pr_name_regex_tuple = [(obj.name, obj.keyword_regex_pattern) for obj in pr_class_list if obj.keyword_regex_pattern is not None]
            pr_assignments_with_keywords_df = assign_prs_with_regex_patterns(non_existing_applicants_no_default_catigory_df, 'Applicant Name', pr_name_regex_tuple)
            print('New assignments made by keyword')
            print(pr_assignments_with_keywords_df)
            pr_assignments_with_keywords_df.to_csv("J:\\Admin & Plans Unit\\Recovery Systems\\1. Systems\\Python Scripts\\Morning Script\\modules\\Assign_Programmatic_Reviewer\\test\\assignments_keyword\\test.csv", index=False)

            # Get remaining accounts (accounts with classifications that do not have default PRs and without keywords in 'Applicant Name')
            merge_columns = ['Grant #','Applicant Name', 'Account Status','FIPS #', 'County', 'Classification', 'PR']
            non_existing_applicants_no_default_catigory_or_keyword = merge_dfs(non_existing_applicants_no_default_catigory_df, pr_assignments_with_keywords_df, merge_columns, 'left', 'left_only')

            # Assign PRs by score (from the above remaining accounts)
            pr_assignments_new_applicants_df = assign_pr_to_new_applcants(non_existing_applicants_no_default_catigory_or_keyword, updated_obj_list, pr_list)
            print('New assignments made by score')
            print(pr_assignments_new_applicants_df)
            # folder_path = 
            pr_assignments_new_applicants_df.to_csv("J:\\Admin & Plans Unit\\Recovery Systems\\1. Systems\\Python Scripts\\Morning Script\\modules\\Assign_Programmatic_Reviewer\\test\\new_applicants\\test.csv", index=False)


            new_assigned_df = append_dfs(appended_currently_assigned_df, pr_assignments_with_classification_df, pr_assignments_with_keywords_df, pr_assignments_new_applicants_df)
            print('This is the new PR assignments list')
            print(new_assigned_df)

            Shira.df_to_csv_replace(new_assigned_df, DESTINATION_FOLDER, file_name)
            
            return

        else:
            Shira.df_to_csv_replace(appended_currently_assigned_df, DESTINATION_FOLDER, file_name)

            return


    get_pr_assignment(ALL_EVENTS, PR_LIST, CLASSIFICATION_REGEX_DICT, KEYWORD_REGEX_DICT, DESTINATION_FOLDER, FLPA_ACCOUNTS)

if __name__ == "__main__":
    main()
