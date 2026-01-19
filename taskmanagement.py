import pandas as pd
from datetime import datetime, date, timedelta
import re
import utils.db as db
import threading



class TaskManagement:

    def __init__(self):
        conn = db.pg_conn()
        schema = db.schema()
        self.epic_df = pd.read_sql_query(f"SELECT * FROM {schema}.epics", conn, dtype=str)
        self.stories_df = pd.read_sql_query(f"SELECT * FROM {schema}.stories", conn, dtype=str)
        self.tasks_df = pd.read_sql_query(f"SELECT * FROM {schema}.tasks", conn, dtype=str)
        self.objectives_df = pd.read_sql_query(f"SELECT * FROM {schema}.objectives", conn, dtype=str)
        self.sprint_dic = self.__create_sprint_dataframe(sprint_days=14, start_date='2024-11-18',sprint_number=100)
        
        self.fulfill_classes()

    @property
    def df_epic(self):
        return self.epic_df
    @property
    def dic_sprint(self):
        return self.sprint_dic
    @property
    def df_stories(self):
        return self.stories_df
    @property
    def df_tasks(self):
        return self.tasks_df
    @property
    def df_objectives(self):
        return self.objectives_df
    @property
    def epics(self):
        return self._epics
    def fulfill_classes(self):
        epic_ids = self.epic_df["id"].tolist()
        self._epics = []

        for ei in epic_ids:
            epic = Epic(epic_id=ei)
            epic.get_attr(self.epic_df)
            epic.get_all_stories(story_df=self.stories_df, task_df=self.tasks_df)
            self._epics.append(epic)

    def complete_task(self, complete_task_id, date):
        self.tasks_df.loc[self.tasks_df['id'] == complete_task_id, ['complitation_date', 'is_completed']] = [date,'true']
        self.save_df( self.tasks_df, 'tasks')
 
    def cancel_task(self, cancel_task_id):
        self.tasks_df.loc[self.tasks_df['id'] == cancel_task_id, ['is_cancelled']] = ['true']
        self.save_df( self.tasks_df, 'tasks')
                        
    def objective_id_by_name(self, objective_name):
        if objective_name == 'No objective':
            return '0'
        else:
            
            return self.objectives_df.loc[self.objectives_df['objective_name']==objective_name, 'objective_id'].values[0]
    
    def tasks_squeeze(self, start_date=date(1900,1,1), end_date=date(2999,1,1), show_all=False):
        squeezed_tasks =[]
        for epic in self.epics:
            for stories in epic.stories:
                for task in stories.tasks:
                    #filter sections
                    if task.is_completed=='true':
                        if start_date <= datetime.strptime(task.complitation_date, "%Y-%m-%d").date():
                            if end_date >= datetime.strptime(task.complitation_date, "%Y-%m-%d").date():
                                squeezed_tasks.append(task)
                    elif show_all:
                        squeezed_tasks.append(task)
        return squeezed_tasks
    def sorted_unique_pi_ids(self):
        unique_pi_ids = [details['pi_id'] for details in  self.dic_sprint.values()]
        unique_pi_ids = list(set(unique_pi_ids))
        unique_pi_ids = [[value, value.split()[1]] for value in  unique_pi_ids]
        sorted_unique_pi_ids = sorted(unique_pi_ids, key= lambda x: int(x[1]))
        sorted_unique_pi_ids = [value[0] for value in sorted_unique_pi_ids]
        return sorted_unique_pi_ids
    def stories_squeeze(self, est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), is_completed=None):
        squeezed_stories = []
        for epic in self.epics:
            for story in epic.stories:
                story_est_start_date = datetime.strptime(story.est_start_date, "%Y-%m-%d").date()
                story_est_end_date = datetime.strptime(story.est_end_date, "%Y-%m-%d").date()
                if story_est_start_date>= est_start_date:
                    if story_est_end_date<=est_end_date:
                        if is_completed==None:
                            squeezed_stories.append(story)
                        if is_completed==True and story.is_completed==True:
                            squeezed_stories.append(story)
                        if is_completed==False and story.is_completed==False:
                            squeezed_stories.append(story)
        return squeezed_stories


    def __add_edit_objective__(self, objective_name, objective_description, objective_due_date, is_life_goal, ac_score, ac_type,
                                life_goal=False, selected_stories=None, objective_id=0, edit=False):
        if is_life_goal:
            is_life_goal_text = 'yes'
            parent_obj = None
            objective_due_date = None
        else:
            is_life_goal_text = 'no'
            parent_obj = self.objective_id_by_name(life_goal)

        if edit:
            self.objectives_df.loc[self.objectives_df['objective_id'] == objective_id, ['objective_name', 'objective_description', 'due_pi', 'is_life_goal',
                                                                                         'parent_object', 'acceptance_criteria_score', 'acceptance_criteria_type']] = [
            objective_name, objective_description, objective_due_date, is_life_goal_text, str(parent_obj), str(ac_score), str(ac_type)]
        else:
            new_objective = {'objective_id':  str(int(self.objectives_df['objective_id'].apply(pd.to_numeric).max())+1),
                            'objective_name': objective_name,
                            'is_life_goal': is_life_goal_text,
                            'parent_object': str(parent_obj),
                            'objective_description': objective_description,
                            'due_pi': str(objective_due_date),
                            'acceptance_criteria_score': str(ac_score),
                            'acceptance_criteria_type': str(ac_type)
                            }
            self.objectives_df = pd.concat([self.objectives_df, pd.DataFrame([new_objective])], ignore_index=True)
        self.save_df( self.objectives_df, 'objectives')
        
        if edit==False:
            if selected_stories!=None and len(selected_stories)>0:
                for st_id in selected_stories:
                    self.edit_story(story_id=st_id, objective_id =new_objective["objective_id"])
        else:
            # remove objectives from stories
            # self.stories_df.loc[self.stories_df['objective_id']==objective_id, 'objective_id'] = '0'
            for st_id in selected_stories:
                self.edit_story(story_id=st_id, objective_id =objective_id)


    def edit_objective(self, objective_id, objective_name, objective_description=None, objective_due_date=None,
                        is_life_goal=None, ac_score=0, ac_type='task', life_goal=False, selected_stories=None, ):
        # find a objective
        if self.__check_objective_uniqness__(objective_name, exception=objective_id):
            self.__add_edit_objective__(objective_name, objective_description, objective_due_date, is_life_goal, ac_score, ac_type, life_goal, selected_stories, objective_id, edit=True)
        else:
            raise ValueError("Objective name must be unique.")
     

    def get_default_ac_score(self,stories, type='story'):

        if type=='story':
            selected_stories = self.stories_df[self.stories_df['id'].isin(stories)]
            ac_score = selected_stories['story_point'].apply(pd.to_numeric).sum()
        elif type=='task':
            selected_tasks = self.tasks_df[self.tasks_df['story_id'].isin(stories)]
            ac_score = selected_tasks['story_id'].apply(pd.to_numeric).count()
        return ac_score
    
    def duplicate_story(self, source_story_id, destination_sprint_id):
        # Find the story in the DataFrame
        for sp_id in destination_sprint_id:

            source_story = self.stories_df[self.stories_df['id'] == source_story_id]
            if not source_story.empty:
                # Create a new story with the same attributes
                new_story = source_story.copy()
            #     print('1----')
                new_story['id'] = str(int(self.stories_df['id'].apply(pd.to_numeric).max()) + 1)
        
                new_story['est_start_date'] = self.dic_sprint[sp_id]['sprint_start_date']
                new_story['est_end_date'] = self.dic_sprint[sp_id]['sprint_end_date']
                new_story['sprint_id'] = str(sp_id)
            #     print('2----')
                # Append the new story to the DataFrame
                self.stories_df = pd.concat([self.stories_df, new_story], ignore_index=True)
                # Find the tasks associated with the source story
                source_tasks = self.tasks_df[self.tasks_df['story_id'] == source_story_id]
                max_task_id = int(self.tasks_df['id'].apply(pd.to_numeric).max())
            #     # Create new tasks with the same attributes

                for  _,task in source_tasks.iterrows():
                    
                    new_task = task.copy()
                    max_task_id += 1

                    new_task['id'] = str(max_task_id)
                    new_task['story_id'] = str(new_story['id'].values[0])
                    new_task['estimate_date'] = 'None'
                    new_task['is_completed'] = 'false'
                    new_task['is_cancelled'] = 'false'
                    new_task['complitation_date'] = 'None'
                    new_task_df = pd.DataFrame([new_task])[self.tasks_df.columns]

                    # # Append the new task to the DataFrame
                    # print(new_task)
                    self.tasks_df = pd.concat([self.tasks_df, new_task_df], ignore_index=True)

                
            self.save_df(self.stories_df, 'stories')
            self.save_df(self.tasks_df, 'tasks')
        return True
    
    def add_objective(self, objective_name, objective_description, objective_due_date, is_life_goal,ac_score=0, ac_type='task', life_goal=False, selected_stories=None):  

# objective_name, objective_description, objective_due_date, is_life_goal, ac_score, ac_type,
#                                 life_goal=False, selected_stories=None, objective_id=0, edit=False)

        # print(objective_name, objective_description, objective_due_date, is_life_goal,ac_score, ac_type, life_goal, selected_stories)
        if self.__check_objective_uniqness__(objective_name):
            self.__add_edit_objective__(objective_name=objective_name, objective_description=objective_description, objective_due_date=objective_due_date, 
                                        is_life_goal=is_life_goal, ac_score=ac_score, ac_type=ac_type,
                                        life_goal=life_goal, selected_stories=selected_stories)
        else:
            raise ValueError("Objective name must be unique.")

    def delete_objective(self, objective_id):
        self.objectives_df = self.objectives_df.loc[self.objectives_df['objective_id']!=objective_id]
        self.stories_df.loc[self.stories_df['objective_id']==objective_id, 'objective_id'] = '0'
        self.save_df(self.stories_df, 'stories')
        self.save_df(self.objectives_df, 'objectives')


    def __check_objective_uniqness__(self, objective_name, exception=None):
        if exception==None:
            filtered_objectives = self.objectives_to_list('objective_name')
        else:
            filtered_objectives = self.objectives_to_list('objective_name', filter_by=f'objective_id!="{exception}"')

        if objective_name in filtered_objectives:
            return False
        else:
            return True
        

    def __safe_df_core__(self, df, table_name):
        conn = db.pg_conn()
        with conn.begin() as connection:
            connection.execute(text(f'TRUNCATE TABLE {db.schema()}.{table_name}'))
            df.to_sql(table_name, connection, if_exists='append', index=False, schema=db.schema())
        print("data has been saved")
        
    def save_df(self, df, table_name):
        self.fulfill_classes()
        thread = threading.Thread(
        target=self.__safe_df_core__,
        args=(df, table_name),
        daemon=True
        )
        thread.start()

        

    def get_story_id_by_name(self, story_name):
        #extract from story_name id for example story name =  'Take a Ride (123)'
        match = re.search(r'\((.*?)\)', story_name)
        if match:
            story_id = match.group(1)
            return str(story_id)
        else:
            return None
        
    def extract_task_id_by_name(self, task_name):
        #extract from task_name id for example task name =  'Take a Ride (123)'
        match = re.search(r'\((.*?)\)', task_name)
        if match:
            task_id = match.group(1)
            return str(task_id)
        else:
            return None
    
    def get_stories_assigned_to_obj(self, objective_name):
        objective_id = self.objective_id_by_name(objective_name)
        return self.stories_to_list('both', filter_by=f'objective_id=="{objective_id}"')
    
    def last_activity(self, start_date, end_date):
        first_iteration = True
        l_activity = None
        tasks = self.tasks_squeeze(start_date=start_date, end_date=end_date)
        for task in tasks:
             comp_date = datetime.strptime(task.complitation_date, "%Y-%m-%d").date()
             if start_date <= comp_date <= end_date:
                if first_iteration:
                    first_iteration = False
                    l_activity = comp_date
                else:
                    t_date = comp_date
                    if t_date>l_activity:
                        l_activity = t_date
        return l_activity
    

    def story_count(self,  est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), options='all_cnt'):
        stories = self.stories_squeeze(est_start_date=est_start_date, est_end_date=est_end_date)

        if options == 'all_cnt':
            return len(stories)
        elif options == 'all_completed_cnt':
            stories_completed = [story for story in stories if story.is_completed]
            return len(stories_completed)
        elif options == 'all_sp':
            i = 0
            for story in stories:
                i = i + int(story.story_point)
            return i
        elif options == 'all_completed_sp':
            i = 0
            for story in stories:
                i = i + int(story.story_point_completed)
            return i

    

    def task_count(self,  est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), is_completed=None):
        stories = self.stories_squeeze(est_start_date=est_start_date, est_end_date=est_end_date)
        i = 0
        for story in stories:
            i = i + story.task_count(is_completed)
        return i

    def add_task_df (self, task_name, story_id, est_dat, task_desc='None'):
        max_task_id = self.tasks_df['id'].apply(pd.to_numeric).max()
        max_task_id = max_task_id + 1
        new_task = {}
        new_task['id'] = str(max_task_id)
        new_task['story_id'] = story_id
        new_task['name'] = task_name
        if isinstance(est_dat, str):
            if str(est_dat)=='None':
                new_task['estimate_date'] = 'None'
            else:
                new_task['estimate_date'] ==  est_dat
        new_task['estimate_date'] = 'None'
        new_task['is_completed'] = 'false'
        new_task['is_cancelled'] = 'false'
        new_task['complitation_date'] = 'None'
        new_task['description'] = task_desc
        new_task_df = pd.DataFrame([new_task])[self.tasks_df.columns]

        # # Append the new task to the DataFrame
        # print(new_task)
        self.tasks_df = pd.concat([self.tasks_df, new_task_df], ignore_index=True)
        self.save_df(self.tasks_df, 'tasks')

    def add_story(self, story_name, story_description, sprint_id, epic_id, story_point, objective_id ='0'):
        new_story = Story(df=self.df_stories)
       
        new_story.name = story_name
        new_story.description = story_description
        new_story.sprint_id = sprint_id
        new_story.epic_id = epic_id
        new_story.story_point = story_point
        new_story.objective_id = objective_id

        max_id = self.stories_df['id'].max()+1
        
        parsed_date = datetime.strptime(self.dic_sprint[sprint_id]["sprint_end_date"], '%Y-%m-%d')
        est_end_date = parsed_date.strftime('%Y-%m-%d')

        parsed_date = datetime.strptime(self.dic_sprint[sprint_id]["sprint_start_date"], '%Y-%m-%d')
        est_start_date = parsed_date.strftime('%Y-%m-%d')


        new_story = {
            "id": max_id,
            "name": story_name,
            "description": story_description,
            "est_start_date": est_start_date,
            "est_end_date": est_end_date,
            "sprint_id": sprint_id,
            "epic_id": epic_id,
            "story_point": story_point,
            "objective_id": objective_id
}

        self.stories_df.loc[len(self.stories_df)] = new_story
        
        self.save_df(self.stories_df, 'stories')
    def edit_story(self, story_id, story_name=None, story_description=None, sprint_id=None, epic_id=None, story_point=None, objective_id =None):
        
        current_story = self.stories_df[self.stories_df['id']==story_id]
        if current_story.empty == False:
            if story_name==None:
                new_story_name = current_story['name'].values[0]
            else:
                new_story_name = story_name
            if story_description==None:
                new_story_description = current_story['description'].values[0]
            else:
                new_story_description = story_description
            if sprint_id==None:
                new_sprint_id = current_story['sprint_id'].values[0]
                est_start_date = self.dic_sprint[new_sprint_id]['sprint_start_date']
                est_end_date = self.dic_sprint[new_sprint_id]['sprint_end_date']

            else:
                new_sprint_id = sprint_id
                est_start_date = self.dic_sprint[new_sprint_id]['sprint_start_date']
                est_end_date = self.dic_sprint[new_sprint_id]['sprint_end_date']
            if epic_id==None:
                new_epic_id = current_story['epic_id'].values[0]
            else:
                new_epic_id = epic_id
            if story_point==None:
                new_story_point = current_story['story_point'].values[0]
            else:
                new_story_point = story_point
            if objective_id==None:
                new_objective_id = current_story['objective_id'].values[0]
            else:
                new_objective_id = objective_id

        self.stories_df.loc[self.stories_df['id'] == story_id, ['name', 'description','est_start_date','est_end_date', 'sprint_id', 'epic_id', 'story_point', 'objective_id']] = [
            new_story_name, new_story_description, est_start_date, est_end_date, new_sprint_id, new_epic_id, new_story_point, new_objective_id]
        self.save_df(self.stories_df, 'stories')
        
        return True
        
    def add_epic(self, epic):
        # create a new epic
        pass

    def epics_to_list(self, field_name):
        if field_name == 'name':
            epic_list = [epic.name for epic in self.epics]
        elif field_name == 'id':
            epic_list = [epic.id for epic in self.epics]
        return epic_list
    
    def objectives_to_list(self, field_name, is_life_goal=None, filter_by=None):
        if filter_by == None:
            return self.df_objectives[field_name].tolist()
        else:
            filtered_df = self.df_objectives.query(filter_by)
            return filtered_df[field_name].tolist()
    

    def stories_to_list(self, field_name, epic_id=None, filter_by=None):
        if filter_by == None:
            if epic_id == None:
                all_stories = self.stories_squeeze()
                if field_name == 'name':
                    story_list = [story.name for story in all_stories]
                elif field_name == 'id':
                    story_list = [story.id for story in all_stories]
                elif field_name =='both':
                    story_list = [f'{story.name} ({story.id})'  for story in all_stories]
            else:
                ep = [epic for epic in self.epics if epic.id == epic_id][0]
                if field_name == 'name':
                    story_list = [story.name for story in ep.stories]
                elif field_name == 'id':
                    story_list = [story.id for story in ep.stories]
                elif field_name =='both':
                    story_list = [f'{story.name} ({story.id})'  for story in ep.stories]
            return story_list
        else:
            # new definition story to list
            if field_name == 'both':
                filtered_df = self.df_stories.query(filter_by)
                story_list = filtered_df.apply(lambda row: f"{row['name']} ({row['id']})", axis=1).tolist()
            else:
                filtered_df = self.df_stories.query(filter_by)
                story_list = filtered_df[field_name].tolist()
               
            return story_list
    def tasks_to_list(self, field_name, story_id):
        
        all_stories = self.stories_squeeze()
        story = [story for story in all_stories if story.id==story_id][0]


        if field_name == 'name':
            tasks_list = [stor.name for stor in story.tasks]
        elif field_name == 'id':
            tasks_list = [stor.id for stor in story.tasks]
        return tasks_list
    def get_objective_by_name(self, objective_name):
        
        return self.df_objectives.query(f'objective_name=="{objective_name}"')
    

    def epic_by_name(self, epic_name):
        return [epic for epic in self.epics if epic.name == epic_name][0]
    

    def epic_by_id(self, epic_id):
        return [epic for epic in self.epics if epic.id == epic_id ][0]
    

    def story_by_name(self, story_name):
        stories = self.stories_squeeze()
        return [story for story in stories if story.name == story_name][0]
    
    def story_by_id(self, story_id):
        stories = self.stories_squeeze()
        return [story for story in stories if story.id == story_id][0]
        
    def save(self, type='All'):

        epic_dic = []
        story_dic = []
        task_dic = []
        epics = self._epics
        for epic in epics:
            dic = {'id': epic.id, 'name': epic.name}
            epic_dic.append(dic)
            for story in epic.stories:
                s_dic = {'epic_id': story.epic_id, 'id': story.id, 'name': story.name, 'description': story.description,
                        'est_start_date': story.est_start_date, 'est_end_date': story.est_end_date,
                         'sprint_id': story.sprint_id, 'story_point': story.story_point,
                         'objective_id': story.objective_id}
                story_dic.append(s_dic)
                for task in story.tasks:
                    t_dic = {'story_id' : task.story_id, 'id': task.id, 'name': task.name,
                             'description': task.description, 'is_completed': task._is_completed,
                             'complitation_date': task.complitation_date, 'is_cancelled': task.is_cancelled,
                             'estimate_date': str(task.estimate_date)}
                    # if task.name=='Take a Ride 2':
                    #     print(str(task.estimate_date))
                    task_dic.append(t_dic)
        if type=='All':
            e_df = pd.DataFrame(epic_dic)
            s_df = pd.DataFrame(story_dic)
            t_df = pd.DataFrame(task_dic)
            self.save_df(e_df, 'epics')
            self.save_df(s_df, 'stories')
            self.save_df(t_df, 'tasks')
        elif type=='tasks':
            t_df = pd.DataFrame(task_dic)
            self.save_df(t_df, 'tasks')
        elif type=='stories':
            s_df = pd.DataFrame(story_dic)
            self.save_df(s_df, 'stories')
        elif type=='epics':
            e_df = pd.DataFrame(epic_dic)
            self.save_df(t_df, 'tasks')
        self.fulfill_classes()
        # save object to database


    def get_pi_end_date(self, pi_id):
        max_date = None
        for sprint, values in self.dic_sprint.items():
            if values["pi_id"] == pi_id:
                if max_date == None:
                    max_date = datetime.strptime( values['sprint_end_date'], "%Y-%m-%d").date()
                else:
                    if max_date < datetime.strptime( values['sprint_end_date'], "%Y-%m-%d").date():
                        max_date = datetime.strptime( values['sprint_end_date'], "%Y-%m-%d").date()        
        return str(max_date)
    
    
    def get_pi_start_date(self, pi_id):
        min_date = None
        for sprint, values in self.dic_sprint.items():
            if values["pi_id"] == pi_id:
                if min_date == None:
                    min_date = datetime.strptime( values['sprint_start_date'], "%Y-%m-%d").date()
                else:
                    if min_date > datetime.strptime( values['sprint_start_date'], "%Y-%m-%d").date():
                        min_date = datetime.strptime( values['sprint_start_date'], "%Y-%m-%d").date()        
        return str(min_date)
    

    def get_current_sprint_pi_id(self, sprint_pi = 'sprint'):
        """
        Return the sprint_id from the DataFrame where today's date is between the start and end dates of the sprint.

        Parameters:
        df (pd.DataFrame): The DataFrame containing sprint information.

        Returns:
        str: The sprint_id of the current sprint, or None if no current sprint is found.
        """
        today = datetime.today().strftime('%Y-%m-%d')
        
        for sprint_id, dates in self.dic_sprint.items():

            if dates['sprint_start_date'] <= today <= dates['sprint_end_date']:
                if sprint_pi=='sprint':
                    return sprint_id
                elif sprint_pi=='pi':
                    return dates["pi_id"]
        return None
    def __create_sprint_dataframe(self, sprint_days,start_date, sprint_number ):
        # Initialize the list to store sprint data
        sprint_data = []
        
        # Set the start date for the first sprint
        start_date =  datetime.strptime(start_date, "%Y-%m-%d")
        
        # Loop to create data for 10 sprints
        for sprint_number in range(1, sprint_number):
            end_date = start_date + timedelta(days=sprint_days - 1)
            if sprint_number<4:
                pi_adj = f"PI 0"
            else:
                pi_adj = f"PI {(sprint_number-4)//5 + 1}"
            sprint_data.append({
                'sprint_id': f"Sprint {sprint_number}",
                'sprint_start_date': start_date.strftime('%Y-%m-%d'),
                'sprint_end_date': end_date.strftime('%Y-%m-%d'),
                'pi_id': pi_adj

            })
            # Update the start date for the next sprint
            start_date = end_date + timedelta(days=1)
        
        sprint_data.insert(0, {'sprint_id': 'Backlog', 'sprint_start_date': '2099-01-01', 'sprint_end_date': '2099-01-01', 'pi_id': 'PI 0'})
        # Create a DataFrame from the sprint data
        df = pd.DataFrame(sprint_data)
    
        return df.set_index('sprint_id').to_dict(orient='index')


class Epic:
    def __init__(self, df=None, epic_id = None):
        if epic_id == None:
            self._id = df['id'].max()+1
        else:
            self._id = epic_id

        self._name = None
        self._stories = []
    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    @property
    def epic_index(self):
        match = re.search(r'\b\d+\b', self.id)
        if match:
            return int(match.group())-1
        else:
            None
    def get_all_stories(self, story_df, task_df):
        story_ids = story_df.loc[story_df["epic_id"] == self.id, "id"].tolist()
        self._stories.clear()
        for story_id in story_ids:
            my_story = Story(story_id=story_id)
            my_story.get_attr(story_df)
            
            my_story.get_all_tasks(task_df)
            self._stories.append(my_story)
    
    def get_attr(self, df):
        self._name = df.loc[df["id"] == self.id, "name"].squeeze() 
    @property
    def stories(self):
        return self._stories
    
class Story:
    def __init__(self, df=None, story_id=None):
        if story_id == None:
            df['id'] = df['id'].astype(int)
            self._id = str(df['id'].max()+1)
        else:
            self._id = story_id

        self._epic_id = None
        self._tasks = []
        self._name = None
        self._description = None
        self._story_point = None
        self._objective_id = '0'
        self._story_index = ''
    @property
    def story_point_index(self):
        if self.story_point == "1":
            return 0
        elif self.story_point == "3":
            return 1
        elif self.story_point == "5":
            return 2
        elif self.story_point == "8":
            return 3
        elif self.story_point == "13":
            return 4                
        elif self.story_point == "21":
            return 5
    @property
    def story_point_completed(self):
        task_count = len(self.tasks)
        i = 0
        for task in self.tasks:
            if task.is_completed=='true':
                i = i + 1
        if i==0:
            return float(0)
        else:
            complitation_percent =  i / task_count
            return float(round(complitation_percent * int(self.story_point), 2))

    @property
    def story_point(self):
        return self._story_point    
    @story_point.setter
    def story_point(self, value):
        self._story_point = value
    @property
    def objective_id(self):
        return self._objective_id    
    @objective_id.setter
    def objective_id(self, value):
        self._objective_id = value

    @property
    def sprint_id(self):
        return self._sprint_id
    
    @sprint_id.setter
    def sprint_id(self, value):
        self._sprint_id = value
        tm = TaskManagement()
        self._est_start_date = tm.dic_sprint[value]["sprint_start_date"]
        self._est_end_date = tm.dic_sprint[value]["sprint_end_date"]

    @property
    def sprint_index(self):
        if self.sprint_id=='Backlog':
            return 0
        else:
            match = re.search(r'\b\d+\b', self._sprint_id)
            if match:
                return int(match.group())-1
            else:
                None

    @property
    def is_completed(self):
        is_compl = True
        for task in self.tasks:
            if task.is_completed=='false':
                is_compl = False
        return is_compl
    @property
    def tasks(self):
        return self._tasks
    @property
    def id(self):
        return self._id
    @property
    def epic_id(self):
        return self._epic_id
    @epic_id.setter
    def epic_id(self, value):
        self._epic_id = value

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, value):
        self._description = value

    @property
    def est_start_date(self):
        return self._est_start_date
    @ est_start_date.setter
    def est_start_date(self, value):
        try:
            # Try to parse the date and format it
            parsed_date = datetime.strptime(value, '%Y-%m-%d')
            self._est_start_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


    @property
    def est_end_date(self):
        return self._est_end_date
    @ est_end_date.setter
    def est_end_date(self, value):
        try:
            # Try to parse the date and format it
            parsed_date = datetime.strptime(value, '%Y-%m-%d')
            self._est_end_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    def get_attr (self, story_df):
            check = story_df.loc[story_df["id"] == self.id, "id"]
            if check.count()==0:
                return False
            else:
                self._name = story_df.loc[story_df["id"] == self.id, "name"].squeeze()
                self._epic_id = story_df.loc[story_df["id"] == self.id, "epic_id"].squeeze()
                self._description = story_df.loc[story_df["id"] == self.id, "description"].squeeze()
                self._est_start_date = story_df.loc[story_df["id"] == self.id, "est_start_date"].squeeze()
                self._est_end_date = story_df.loc[story_df["id"] == self.id, "est_end_date"].squeeze()
                self._sprint_id = story_df.loc[story_df["id"] == self.id, "sprint_id"].squeeze()
                self._story_point = story_df.loc[story_df["id"] == self.id, "story_point"].squeeze()
                self._objective_id = story_df.loc[story_df["id"] == self.id, "objective_id"].squeeze()
                return True


    def get_all_tasks(self, df):
        task_ids = df.loc[df["story_id"] == self.id, "id"].tolist()
        self._tasks.clear()
        for task in task_ids:
            my_task = Task(task_id=task)
            my_task.get_attr(df)
            self._tasks.append(my_task)
    
    def task_count(self, is_completed=None):
        i = 0
        for task in self.tasks:
            if task.is_completed=='true' and is_completed==True:
                i = i + 1
            elif is_completed==None:
                i = i + 1
            elif task.is_completed=='false' and is_completed==False:
                i = i + 1            
        return i

class Task:
    def __init__(self,task_id=None, task_name=None, task_desc=None, df=None, est_date=None):
        if task_id == None:
            df['id'] = df['id'].astype(int)
            self._id = str(df['id'].max()+1)
        else:
            self._id = task_id
        self._story_id = None
        self._name = task_name
        self._description = task_desc
        self._is_completed = 'false'
        self._complitation_date = None
        self._is_cancelled = 'false'
        if isinstance(est_date, str):
            if str(est_date)=='None':
                self._estimate_date = None
            else:
                self._estimate_date =  datetime.strptime(est_date, '%Y-%m-%d').date()
        else:
            self._estimate_date = est_date

    @property
    def estimate_date(self):
        return self._estimate_date

    @estimate_date.setter
    def estimate_date(self, value):
        if str(value)== 'None':
            self._estimate_date = None
        elif isinstance(value, str):
            self._estimate_date = datetime.strptime(value, '%Y-%m-%d').date()
    
    @property
    def story_id(self):
        return self._story_id
    
    @story_id.setter
    def story_id(self, value):
        self._story_id = value

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,value):
        self._name=value
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self,value):
        self._description = value
    
    @property
    def is_completed(self):
        return self._is_completed

    @property   
    def complitation_date(self):
        return self._complitation_date
    
    @complitation_date.setter   
    def complitation_date(self, value):
        self._complitation_date = value
        if  value !=None:    
            self._is_completed = 'true'
        else:
            self._is_completed = 'false'

    @property
    def is_cancelled(self):
        return self._is_cancelled
    
    @is_cancelled.setter
    def is_cancelled(self, value):
        self._is_cancelled = value
    
    def get_attr(self, df):
            check = df.loc[df["id"] == self.id, "id"]
            if check.count()==0:
                return False
            else:
                self._name = df.loc[df["id"] == self.id, "name"].squeeze()
                self._story_id = df.loc[df["id"] == self.id, "story_id"].squeeze()
                self._description = df.loc[df["id"] == self.id, "description"].squeeze()
                self._is_completed = df.loc[df["id"] == self.id, "is_completed"].squeeze()
                self._is_cancelled = df.loc[df["id"] == self.id, "is_cancelled"].squeeze()
                self._complitation_date = df.loc[df["id"] == self.id, "complitation_date"].squeeze()
                self.estimate_date = df.loc[df["id"] == self.id, "estimate_date"].squeeze()


if __name__ =='__main__':
    # !!!!! CREATE A INNITIAL DATABASE !!!!
    # conn = db.pg_conn()
    # epic_df.to_sql('epics', conn, if_exists='replace', index=False)
    # stories_df.to_sql('stories', conn, if_exists='replace', index=False)
    # tasks_df.to_sql('tasks', conn, if_exists='replace', index=False)
    # conn.close()

# epic_df = pd.read_csv("data/epics.csv")
# stories_df = pd.read_csv("data/stories.csv")
# tasks_df = pd.read_csv("data/tasks.csv")




    # print(tasks_df)
    tasktm = TaskManagement()

    
    # be.send_email_with_attachment(
    #     body='Please find the attached file.',
    #     attachment_path='data/database.db'
    #     )


    # print(tm.story_count())
    # for task in tm.tasks_squeeze(show_all=True):
    #     print (task.name)

    # print (tm.last_activity())



    # print(tasks_df)

    # for epic in tm.epics:
    #     for story in epic.stories:
    #         for task in story.tasks:
    #             print(f'task id: {task.id} - story.id: {task.story_id} epic {epic.id}')

    # print(tm.epics[0].stories[0].tasks[0].complitation_date)
    # tm.epics[0].stories[0].tasks[0].complitation_date = '2024-10-25'
    # tm.epics[0].stories[0].tasks[1].complitation_date = '2024-10-24'
    # tm.epics[0].stories[0].tasks[3].complitation_date = '2024-10-20'
    # tm.epics[0].stories[0].tasks[4].complitation_date = '2024-10-21'


    # # print(tm.epics[0].stories[0].tasks[0].complitation_date)

    # print(f"epic: {tm.epics[0].name}")
    # print(f"story: {tm.epics[0].stories[s_id-1].name}")
    # print(f"task: {tm.epics[0].stories[s_id-1].tasks[t_id-1].name}")



